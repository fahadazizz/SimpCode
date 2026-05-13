from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Callable, Optional

from pydantic import BaseModel
import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from simpcode.core.analyzer import ProjectAnalyzer
from simpcode.core.evolution import GetBetter
from simpcode.core.generator import IntelligenceSynthesizer
from simpcode.core.llm import LLMClient
from simpcode.core.modes import ScanScene
from simpcode.core.onboarding import ensure_onboarding_artifacts, needs_onboarding
from simpcode.core.paths import get_plans_dir, get_project_root
from simpcode.core.planner import Plan, PlanGenerator
from simpcode.core.executor import TakeAction
from simpcode.core.prompts import registry
from simpcode.core.state import SessionManager, SessionMessage, SessionState
from simpcode.harness.permissions import PermissionSystem
from simpcode.wiki.bootstrap import WikiBootstrap
from simpcode.wiki.engine import WikiEngine


class SimpWorkflows:
    """Shared command orchestration for both the CLI and the TUI."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def _make_llm(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> LLMClient:
        return LLMClient(provider=provider, model_id=model)

    def _confirm(self, prompt_fn: Optional[Callable[[str], str]], message: str) -> bool:
        prompt = prompt_fn or self.console.input
        return prompt(message).strip().lower() in {"y", "yes"}

    def _ensure_onboarded(
        self,
        root: Path,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> bool:
        if not needs_onboarding(root):
            return False

        analyzer = ProjectAnalyzer(root)
        with self.console.status("[bold blue]Collecting codebase metadata..."):
            metadata = analyzer.collect_metadata()

        # Detection: If no significant manifests or entry points, it's a skeleton
        is_skeleton = len(metadata.manifests) == 0 and len(metadata.entry_point_samples) == 0

        if is_skeleton:
            with self.console.status("[bold blue]Initializing Project Skeleton..."):
                ensure_onboarding_artifacts(root)
                self.console.print("\n[bold green]✓ Skeleton Initialization Complete.[/bold green]")
                return True

        # Legacy Import (Synthesis Required)
        llm = self._make_llm(provider=provider, model=model)
        synthesizer = IntelligenceSynthesizer(llm)
        bootstrap = WikiBootstrap(llm, root)

        try:
            with self.console.status("[bold blue]Synthesizing Project Intelligence..."):
                docs = synthesizer.synthesize(metadata)

            with self.console.status("[bold blue]Compiling Initial Wiki (Semantic Core)..."):
                try:
                    bootstrap.run(metadata)
                except Exception as bootstrap_error:
                    self.console.print(
                        f"[yellow]Wiki bootstrap degraded:[/yellow] {bootstrap_error}"
                    )

            ensure_onboarding_artifacts(root, docs, metadata)
            self.console.print("\n[bold green]✓ Legacy Import & Synthesis Complete.[/bold green]")
        except Exception as e:
            self.console.print(f"[red]Synthesis failed:[/red] {e}")
            self.console.print("[yellow]Falling back to skeleton initialization...[/yellow]")
            ensure_onboarding_artifacts(root)
            self.console.print("\n[bold green]✓ Fallback Initialization Complete.[/bold green]")

        return True

    def init_project(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Path:
        root = get_project_root()
        self._ensure_onboarded(root, provider=provider, model=model)
        return root

    def ask(
        self,
        question: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        root = get_project_root()
        self._ensure_onboarded(root, provider=provider, model=model)

        llm = self._make_llm(provider=provider, model=model)
        scanner = ScanScene(root, llm)

        with self.console.status("[bold blue]Scanning scene and navigating Wiki..."):
            context = scanner.run(question)

        with self.console.status("[bold blue]Reasoning..."):
            instruction = registry.load("research_assistant")
            response = llm.chat(
                [{"role": "user", "content": f"CONTEXT:\n{context}\n\nQUERY: {question}"}],
                instruction,
            )

        self.console.print(
            Panel(Markdown(response), title="SimpCode Analysis", border_style="green")
        )
        return response

    def do(
        self,
        task: str,
        yes: bool = False,
        dry_run: bool = False,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        approval_prompt: Optional[Callable[[str], str]] = None,
    ) -> Plan:
        root = get_project_root()
        self._ensure_onboarded(root, provider=provider, model=model)

        llm = self._make_llm(provider=provider, model=model)
        scanner = ScanScene(root, llm)
        planner = PlanGenerator(llm, scanner)
        permissions = PermissionSystem(self.console)
        session_id = f"task_{int(time.time())}"
        executor = TakeAction(root, llm, session_id=session_id)
        evolver = GetBetter(root, llm)

        with self.console.status("[bold blue]Scanning impact surface..."):
            context = scanner.run(task)

        with self.console.status("[bold blue]Thinking Through (Planning)..."):
            plan = planner.generate(task, context)
            plan.task_id = session_id

        plan_path = get_plans_dir() / f"plan_{session_id}.json"
        plan_path.write_text(plan.model_dump_json(indent=2))

        if dry_run:
            permissions.review_plan(plan, prompt_fn=approval_prompt)
            self.console.print("\n[yellow]Dry-run complete. No changes made.[/yellow]")
            return plan

        approved = yes or permissions.review_plan(plan, prompt_fn=approval_prompt)

        if approved:
            self.console.print(
                "\n[bold green]Plan Approved. Transitioning to TAKE ACTION.[/bold green]"
            )
            execution_trace = executor.execute(plan, context)

            with self.console.status("[bold blue]Getting Better (Reflecting)..."):
                proposals = evolver.run(task, execution_trace)

            if proposals:
                has_elements = (
                    proposals.new_patterns
                    or proposals.new_risks
                    or proposals.new_invariants
                )
                if has_elements:
                    self.console.print("\n[bold magenta]Evolution Proposals Discovered[/bold magenta]")
                    if proposals.new_patterns:
                        self.console.print(f"[cyan]Patterns:[/cyan] {proposals.new_patterns}")
                    if proposals.new_risks:
                        self.console.print(f"[cyan]Risks:[/cyan] {proposals.new_risks}")
                    if proposals.new_invariants:
                        self.console.print(f"[cyan]Invariants:[/cyan] {proposals.new_invariants}")

                    if self._confirm(approval_prompt, "\nDo you want to append these insights to the Wiki? (y/n): "):
                        with self.console.status("Saving Evolution Insights..."):
                            evolver.append_proposals(proposals)
                            self.console.print(
                                "[green]✓ Insights integrated into the cognitive layers.[/green]"
                            )

            self.console.print("\n[bold green]✓ Task lifecycle complete.[/bold green]")
        else:
            self.console.print("\n[red]Task Aborted by User.[/red]")

        return plan

    def sync(self) -> None:
        root = get_project_root()
        wiki = WikiEngine(root)
        llm = self._make_llm()

        self.console.print("[bold blue]Synchronizing Wiki with Source Truth...[/bold blue]")

        pages = wiki.get_all_pages()
        stale_count = 0

        for page in pages:
            stale_sources = wiki.check_staleness(page)
            if stale_sources:
                stale_count += 1
                self.console.print(
                    f"Page [yellow]{page.metadata.id}[/yellow] is stale. Regenerating..."
                )

                with self.console.status(f"Compiling {page.metadata.id}..."):
                    code_context = ""
                    for source, current_hash in stale_sources:
                        full_path = root / source.file_path
                        if full_path.exists():
                            code_context += (
                                f"--- {source.file_path} ---\n"
                                f"{full_path.read_text()[:5000]}\n"
                            )
                        source.hash = current_hash

                    instruction = registry.load("wiki_maintainer")
                    prompt = (
                        f"OLD CONTENT:\n{page.content}\n\n"
                        f"Current Code:\n{code_context}\n\nUpdate page."
                    )
                    page.content = llm.chat([{"role": "user", "content": prompt}], instruction)
                    page.metadata.last_updated = time.time()
                    wiki.save_page(page)
                    self.console.print(f"  [green]✓[/green] Synchronized {page.metadata.id}")

        if stale_count == 0:
            self.console.print("[green]Wiki is consistent with codebase.[/green]")
        else:
            self.console.print("\n[bold green]Synchronization complete.[/bold green]")

    def status(self) -> None:
        root = get_project_root()
        wiki = WikiEngine(root)

        self.console.print(
            Panel(
                f"Project: [bold]{root.name}[/bold]\nRoot: {root}",
                title="SIMPCODE STATUS",
                border_style="cyan",
            )
        )

        pages = wiki.get_all_pages()
        stale_pages = [p for p in pages if wiki.is_page_stale(p)]

        table = Table(show_header=False, box=None)
        table.add_row("Wiki Pages:", f"{len(pages)}")
        table.add_row(
            "Stale Pages:",
            f"[bold red]{len(stale_pages)}[/bold red]" if stale_pages else "[green]0[/green]",
        )
        self.console.print(table)

        if stale_pages:
            self.console.print("\n[yellow]Stale Knowledge Detected:[/yellow]")
            for page in stale_pages:
                self.console.print(f"  - {page.metadata.id}")
            self.console.print("\nRun `simp sync` to restore consistency.")

    def recover(self, approval_prompt: Optional[Callable[[str], str]] = None) -> None:
        root = get_project_root()
        plans_dir = get_plans_dir()
        plans = list(plans_dir.glob("*.json"))

        if not plans:
            self.console.print("[yellow]No recoverable sessions found.[/yellow]")
            return

        latest_plan_file = max(plans, key=lambda path: path.stat().st_mtime)
        self.console.print(
            f"[bold blue]Recovery Mode:[/bold blue] Loading session {latest_plan_file.name}"
        )

        plan_data = json.loads(latest_plan_file.read_text())
        plan = Plan(**plan_data)

        permissions = PermissionSystem(self.console)
        if permissions.review_plan(plan, prompt_fn=approval_prompt):
            llm = self._make_llm()
            executor = TakeAction(root, llm, session_id=plan.task_id)
            executor.execute(
                plan,
                "RECOVERY CONTEXT: Session restored from persisted plan artifact.",
            )
            self.console.print("[bold green]✓ Session Recovery Successful.[/bold green]")

    def update_simp(
        self,
        instruction: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        approval_prompt: Optional[Callable[[str], str]] = None,
    ) -> str:
        root = get_project_root()
        llm = self._make_llm(provider=provider, model=model)
        analyzer = ProjectAnalyzer(root)
        metadata = analyzer.collect_metadata()
        simp_path = root / "SIMP.md"
        current_simp = simp_path.read_text() if simp_path.exists() else ""

        prompt = registry.load("simp_update", include_base=False).format(
            project_name=metadata.name,
            root=metadata.root,
            current_simp=current_simp,
            instruction=instruction,
            file_tree=metadata.file_tree,
            manifests=metadata.manifests,
        )

        system_instruction = registry.load("base_principles")

        class SimpDraft(BaseModel):
            simp_md: str

        draft = llm.structured_output(prompt, SimpDraft, system_instruction)
        updated = draft.simp_md.strip()
        if not updated:
            raise RuntimeError("SIMP update produced empty content.")

        self.console.print(Panel(updated, title="Proposed SIMP.md", border_style="magenta"))
        if not self._confirm(approval_prompt, "Apply this SIMP.md update? (y/n): "):
            self.console.print("[yellow]SIMP.md update cancelled.[/yellow]")
            return current_simp

        simp_path.write_text(updated + "\n")
        self.console.print(f"[bold green]✓ SIMP.md updated at {simp_path}[/bold green]")
        return updated

    def wiki_show(self, page_id: str) -> None:
        root = get_project_root()
        wiki = WikiEngine(root)
        page = wiki.get_page(page_id)
        if page:
            self.console.print(
                Panel(
                    page.content,
                    title=f"WIKI: {page_id}",
                    subtitle=(
                        f"Type: {page.metadata.type} | Last Updated: {time.ctime(page.metadata.last_updated)}"
                    ),
                )
            )
        else:
            self.console.print(f"[red]Error: Knowledge node '{page_id}' not found.[/red]")

    def wiki_list(self) -> None:
        root = get_project_root()
        wiki = WikiEngine(root)
        pages = wiki.get_all_pages()

        table = Table(title="Knowledge Graph (Wiki)")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Freshness", justify="center")

        for page in pages:
            freshness = "[red]STALE[/red]" if wiki.is_page_stale(page) else "[green]FRESH[/green]"
            table.add_row(page.metadata.id, page.metadata.type, freshness)

        self.console.print(table)

    def chat_turn(
        self,
        state: SessionState,
        manager: SessionManager,
        llm: LLMClient,
        user_input: str,
    ) -> str:
        root = Path(state.project_root)
        scanner = ScanScene(root, llm)

        with self.console.status("[bold blue]Thinking..."):
            context = scanner.run(user_input)
            instruction = registry.load("interactive_assistant")

            messages = [{"role": message.role, "content": message.content} for message in state.history]
            full_user_input = f"LOCAL CONTEXT:\n{context}\n\nUSER: {user_input}"
            chat_payload = messages + [{"role": "user", "content": full_user_input}]
            response = llm.chat(chat_payload, instruction)

        state.history.append(SessionMessage(role="user", content=user_input))
        state.history.append(SessionMessage(role="assistant", content=response))
        manager.save_session(state)

        self.console.print(Panel(Markdown(response), title="SimpCode", border_style="green"))
        return response
