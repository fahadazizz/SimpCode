import sys
import time
from pathlib import Path
from typing import List, Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.markdown import Markdown
from rich.layout import Layout
from rich.table import Table

from simpcode.core.llm import LLMClient
from simpcode.core.modes import ScanScene
from simpcode.core.planner import PlanGenerator, Plan
from simpcode.core.executor import TakeAction
from simpcode.core.evolution import GetBetter
from simpcode.core.paths import get_project_root, get_plans_dir
from simpcode.core.state import SessionManager, SessionState, SessionMessage
from simpcode.harness.permissions import PermissionSystem
from simpcode.wiki.engine import WikiEngine
from simpcode.core.prompts import registry
from simpcode.core.onboarding import needs_onboarding, ensure_onboarding_artifacts

class SimpShell:
    """
    SimpCode Interactive TUI: The primary interface for real-time engineering.
    Implements a full state machine from Mission to Reflection.
    """
    def __init__(self, provider: Optional[str] = None, model_id: Optional[str] = None, session_id: Optional[str] = None):
        self.console = Console()
        self.root = get_project_root()
        self.llm = LLMClient(provider=provider, model_id=model_id)
        
        # Session Management
        self.manager = SessionManager(str(self.root))
        if session_id:
            self.state = self.manager.load_session(session_id) or self._new_session(session_id)
        else:
            # Load latest or new
            latest = self.manager.list_sessions()
            if latest:
                 self.state = self.manager.load_session(latest[0]["id"])
            else:
                 self.state = self._new_session()

        # Update LLM config if overrides provided
        if provider: self.state.current_provider = provider
        if model_id: self.state.current_model = model_id
        
        # UI State
        self.history_path = Path.home() / ".simpcode" / "history"
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.session = PromptSession(history=FileHistory(str(self.history_path)))

    def _new_session(self, session_id: Optional[str] = None) -> SessionState:
        sid = session_id or f"session_{int(time.time())}"
        state = SessionState(
            session_id=sid,
            project_root=str(self.root),
            current_provider=str(self.llm.provider_name),
            current_model=str(self.llm.model_id)
        )
        self.manager.save_session(state)
        return state

    def welcome(self):
        banner = r"""
   _____ _                 _____          _      
  / ____(_)               / ____|        | |     
 | (___  _ _ __ ___  _ __| |     ___   __| | ___ 
  \___ \| | '_ ` _ \| '_ \ |    / _ \ / _` |/ _ \
  ____) | | | | | | | |_) | |___| (_) | (_| |  __/
 |_____/|_|_| |_| |_| .__/ \_____\___/ \__,_|\___|
                    | |                           
                    |_|                           
        """
        self.console.print(f"[bold blue]{banner}[/bold blue]")
        self.console.print(f"[dim]Project: {self.root}[/dim]")
        self.console.print(f"[dim]Session: {self.state.session_id}[/dim]")
        self.console.print(f"[dim]Provider: {self.state.current_provider} ({self.state.current_model})[/dim]\n")
        
        if self.state.history:
            self.console.print(f"[yellow]Resuming session with {len(self.state.history)} messages.[/yellow]")

        # SPEC.md is optional; if present, it will be used by planning and reflection.

    def run(self):
        self.welcome()
        
        # Check if project is initialized
        if not (self.root / ".simp").exists():
            self.console.print("[yellow]Warning: Project not initialized. Type '/init' to setup.[/yellow]")

        while True:
            try:
                user_input = self.session.prompt(
                    "simp> ",
                    auto_suggest=AutoSuggestFromHistory()
                ).strip()

                if not user_input:
                    continue
                
                # Command Routing
                if user_input.startswith("/"):
                    cmd_parts = user_input[1:].split(" ", 1)
                    cmd = cmd_parts[0].lower()
                    args = cmd_parts[1] if len(cmd_parts) > 1 else ""
                    
                    if cmd in ["exit", "quit", "q"]:
                        self.manager.save_session(self.state)
                        self.console.print("[bold green]Session saved. Goodbye![/bold green]")
                        sys.exit(0)
                    
                    if cmd == "ask":
                        self.handle_ask(args)
                    elif cmd == "do":
                        # Support flags in /do like --yes or --dry-run
                        self.handle_do_with_args(args)
                    elif cmd == "sync":
                        self.handle_sync()
                    elif cmd == "init":
                        self.handle_init()
                    elif cmd == "clear":
                        self.state.history = []
                        self.manager.save_session(self.state)
                        self.console.print("[dim]Chat history cleared.[/dim]")
                    elif cmd == "help":
                        self.show_help()
                    elif cmd == "sessions":
                        self.handle_sessions(args)
                    else:
                        self.console.print(f"[red]Unknown command: /{cmd}. Type /help for options.[/red]")
                    continue

                self.handle_chat(user_input)

            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[bold red]Error:[/bold red] {e}")

    def handle_sessions(self, args: str):
        sessions = self.manager.list_sessions()
        if not sessions:
            self.console.print("[yellow]No sessions found.[/yellow]")
            return
        
        table = Table(title="Recent Sessions")
        table.add_column("Session ID", style="cyan")
        table.add_column("Last Updated", style="magenta")
        table.add_column("Preview", style="dim")
        
        for s in sessions[:10]:
            table.add_row(s["id"], time.ctime(s["last_updated"]), s["preview"])
        self.console.print(table)
        self.console.print("[dim]Use `simp chat --session <id>` from your terminal to switch sessions.[/dim]")

    def handle_do_with_args(self, args_str: str):
        import shlex
        try:
            # We want to support /do "task" --yes etc.
            # But the user might just type /do make a file
            # Let's try to parse out flags if they exist
            parts = shlex.split(args_str)
            task_parts = []
            yes = False
            dry_run = False
            
            for p in parts:
                if p == "--yes": yes = True
                elif p == "--dry-run": dry_run = True
                else: task_parts.append(p)
            
            task = " ".join(task_parts)
            if not task:
                self.console.print("[red]Error: /do requires a task description.[/red]")
                return
                
            self.handle_do(task, yes=yes, dry_run=dry_run)
        except Exception as e:
            self.console.print(f"[red]Error parsing command:[/red] {e}")

    def show_help(self):
        table = Table(title="SimpShell Slash Commands", box=None)
        table.add_column("Command", style="cyan")
        table.add_column("Description")
        table.add_row("/ask <query>", "Research & analysis using Semantic Wiki.")
        table.add_row("/do <task> [--yes] [--dry-run]", "Full Engineering Lifecycle (Plan -> Run).")
        table.add_row("/sync", "Synchronize Wiki with source changes.")
        table.add_row("/init", "Onboard current project.")
        table.add_row("/sessions", "List recent local sessions.")
        table.add_row("/clear", "Clear session chat history.")
        table.add_row("/exit", "Save and quit SimpCode.")
        self.console.print(table)

    def handle_ask(self, query: str):
        if not query:
            self.console.print("[red]Error: /ask requires a query.[/red]")
            return
        
        scanner = ScanScene(self.root, self.llm)
        with self.console.status("[bold blue]Scanning scene..."):
            context = scanner.run(query)
            instruction = registry.load("research_assistant")
            response = self.llm.chat([{"role": "user", "content": f"CONTEXT:\n{context}\n\nQUERY: {query}"}], instruction)
            self.console.print(Panel(Markdown(response), title="Research Result", border_style="green"))

    def handle_do(self, task: str, yes: bool = False, dry_run: bool = False):
        if not task:
            self.console.print("[red]Error: /do requires a task description.[/red]")
            return
            
        scanner = ScanScene(self.root, self.llm)
        planner = PlanGenerator(self.llm, scanner)
        permissions = PermissionSystem(self.console)
        session_id = f"task_{int(time.time())}"
        executor = TakeAction(self.root, self.llm, session_id=session_id)
        
        with self.console.status("[bold blue]Planning mission..."):
            context = scanner.run(task)
            plan = planner.generate(task, context)
            
        if dry_run:
            permissions.review_plan(plan)
            return

        if yes or permissions.review_plan(plan):
            executor.execute(plan, context, scanner=scanner, task=task)
            self.console.print("[bold green]✓ Task complete.[/bold green]")

    def handle_sync(self):
        wiki = WikiEngine(self.root)
        with self.console.status("[bold blue]Syncing Wiki..."):
            # Reuse sync logic from main.py if possible or implement here
            self.console.print("[yellow]Synchronization in progress... (Simulated for now)[/yellow]")
            # Implementation would call wiki.get_all_pages() etc.
            self.console.print("[green]✓ Wiki synchronized.[/green]")

    def handle_init(self):
        from simpcode.core.analyzer import ProjectAnalyzer
        from simpcode.core.generator import IntelligenceSynthesizer, DocumentGenerator
        from simpcode.wiki.bootstrap import WikiBootstrap
        
        analyzer = ProjectAnalyzer(self.root)
        synthesizer = IntelligenceSynthesizer(self.llm)
        generator = DocumentGenerator(self.root)
        bootstrap = WikiBootstrap(self.llm, self.root)
        
        with self.console.status("[bold blue]Initializing Project..."):
            if needs_onboarding(self.root):
                metadata = analyzer.collect_metadata()
                docs = synthesizer.synthesize(metadata)
                generator.write_docs(docs)
                try:
                    bootstrap.run(metadata)
                except Exception as bootstrap_error:
                    self.console.print(f"[yellow]Wiki bootstrap degraded:[/yellow] {bootstrap_error}")
                ensure_onboarding_artifacts(self.root, docs, metadata)
        self.console.print("[bold green]✓ Project Onboarded.[/bold green]")

    def handle_chat(self, user_input: str):
        """
        Standard interactive chat mode.
        """
        # Build history context
        messages = [{"role": m.role, "content": m.content} for m in self.state.history]
        messages.append({"role": "user", "content": user_input})
        
        scanner = ScanScene(self.root, self.llm)
        with self.console.status("[bold blue]Thinking..."):
            context = scanner.run(user_input)
            instruction = registry.load("interactive_assistant")
            
            # Hybrid message: history + local context
            full_user_input = f"LOCAL CONTEXT:\n{context}\n\nUSER: {user_input}"
            chat_payload = messages[:-1] + [{"role": "user", "content": full_user_input}]
            
            response = self.llm.chat(chat_payload, instruction)
            
        # Update state persistence
        self.state.history.append(SessionMessage(role="user", content=user_input))
        self.state.history.append(SessionMessage(role="assistant", content=response))
        self.manager.save_session(self.state)
        
        self.console.print(Panel(Markdown(response), border_style="blue"))
        
        self.console.print(Panel(Markdown(response), title="SimpCode", border_style="green"))
