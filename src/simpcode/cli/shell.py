import shlex
import sys
import time
from pathlib import Path
from typing import Optional, List

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from simpcode.core.llm import LLMClient
from simpcode.core.paths import get_project_root
from simpcode.utils.paths import PathManager
from simpcode.core.state import SessionManager, SessionMessage, SessionState
from simpcode.core.workflows import SimpWorkflows


from prompt_toolkit.styles import Style

# ---------------------------------------------------------------------------
# TUI Styling (Zen)
# ---------------------------------------------------------------------------
SIMP_STYLE = Style.from_dict({
    "prompt": "bold #00afff",
    "status": "italic #888888",
    "command": "bold #ff00ff",
    "file": "#00ffaf",
    "wiki": "#ffff00",
})

# ---------------------------------------------------------------------------
# Command Registry
# ---------------------------------------------------------------------------
COMMANDS = {
    "ask": "Research the codebase using Wiki context",
    "do": "Plan and execute a task [--yes] [--dry-run]",
    "sync": "Synchronize wiki with source code",
    "status": "Show project and wiki health",
    "recover": "Restore the latest recoverable plan",
    "init": "Onboard current project",
    "wiki": "Manage knowledge base (list|show|search)",
    "config": "LLM configuration (--provider|--model)",
    "sessions": "Manage sessions (--switch|--export)",
    "simp": "Show or update SIMP.md (show|update)",
    "clear": "Clear chat history [--full]",
    "help": "Show command reference [command]",
    "exit": "Save and quit",
}


# ---------------------------------------------------------------------------
# Smart Completer: /, @, #
# ---------------------------------------------------------------------------
class SimpCompleter(Completer):
    """
    Context-aware completer for the SimpCode TUI.
      /  → slash commands
      @  → project files
      #  → wiki pages
    """

    def __init__(self, root: Path, wiki_dir: Path):
        self.root = root
        self.wiki_dir = wiki_dir
        self._file_cache: Optional[List[str]] = None
        self._file_cache_ts: float = 0.0

    # -- file tree (cached for 10 s) --
    def _project_files(self) -> List[str]:
        now = time.time()
        if self._file_cache is not None and now - self._file_cache_ts < 10:
            return self._file_cache

        files: List[str] = []
        skip = {".git", ".simp", ".simpcode", "__pycache__", "node_modules", ".venv", "venv"}
        try:
            for p in self.root.rglob("*"):
                if p.is_file() and not any(part in skip for part in p.parts):
                    rel = str(p.relative_to(self.root))
                    files.append(rel)
        except Exception:
            pass

        self._file_cache = sorted(files)[:500]  # cap to avoid perf issues
        self._file_cache_ts = now
        return self._file_cache

    # -- wiki pages --
    def _wiki_pages(self) -> List[str]:
        pages: List[str] = []
        if self.wiki_dir.exists():
            for p in self.wiki_dir.rglob("*.md"):
                pages.append(p.stem)
        return sorted(set(pages))

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        word = document.get_word_before_cursor(WORD=True)

        # Slash command completion
        if text.lstrip().startswith("/"):
            cmd_prefix = text.lstrip()[1:].split()[0] if text.strip() != "/" else ""
            if " " not in text.lstrip()[1:]:
                for cmd, desc in COMMANDS.items():
                    if cmd.startswith(cmd_prefix):
                        yield Completion(
                            cmd,
                            start_position=-len(cmd_prefix),
                            display_meta=desc,
                        )
            return

        # @file completion
        if "@" in word:
            prefix = word.split("@", 1)[1]
            for f in self._project_files():
                if f.lower().startswith(prefix.lower()):
                    yield Completion(f, start_position=-len(prefix))
            return

        # #wiki completion
        if "#" in word:
            prefix = word.split("#", 1)[1]
            for page in self._wiki_pages():
                if page.lower().startswith(prefix.lower()):
                    yield Completion(page, start_position=-len(prefix))
            return


# ---------------------------------------------------------------------------
# SimpShell – Zen TUI
# ---------------------------------------------------------------------------
class SimpShell:
    """
    SimpCode Interactive TUI (The Zen Shell).
    Stream-first interaction model with rich context completion.
    """

    def __init__(
        self,
        root: Optional[Path] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        self.console = Console()
        self.root = root or PathManager.find_project_root()
        self.wiki_dir = self.root / ".simp" / "wiki"
        self.workflows = SimpWorkflows(self.console)
        
        # Session Management
        self.session_manager = SessionManager(self.root)
        if session_id:
            self.state = self.session_manager.load_session(session_id)
        else:
            self.state = self.session_manager.get_latest_session() or self.session_manager.create_session()
        
        # Override if provided
        if provider: self.state.current_provider = provider
        if model: self.state.current_model = model
        
        self.session_manager.save_session(self.state)
        
        # History Setup
        self.history_path = PathManager.resolve_writable_path(self.root, "history")
        self.history = FileHistory(str(self.history_path)) if self.history_path else InMemoryHistory()
        
        # TUI Components
        self.completer = SimpCompleter(self.root, self.wiki_dir)
        self.session = PromptSession(
            history=self.history,
            completer=self.completer,
            complete_while_typing=True,
            style=SIMP_STYLE
        )

    # ── helpers ────────────────────────────────────────────────────────────

    def _refresh_llm(self) -> LLMClient:
        return LLMClient(
            provider=self.state.current_provider,
            model_id=self.state.current_model,
        )

    # ── status line (one-liner) ────────────────────────────────────────────

    def _render_status_line(self) -> str:
        """Compact, single-line status string."""
        project = self.root.name
        provider = self.state.current_provider
        model = self.state.current_model
        # Truncate model to keep line short
        model_short = model if len(model) <= 24 else model[:22] + "…"
        has_wiki = "●" if (self.root / ".simp" / "wiki").exists() else "○"
        return f"[dim]{project}[/dim]  [cyan]{provider}[/cyan]/{model_short}  {has_wiki} wiki"

    # ── welcome ────────────────────────────────────────────────────────────

    def welcome(self):
        """Compact welcome: one-line banner + status + context hint."""
        self.console.print()
        self.console.print(
            "[bold blue]╭─ SimpCode[/bold blue] [dim]· High-Integrity Agentic Engineering[/dim]"
        )
        self.console.print(f"[bold blue]╰─[/bold blue] {self._render_status_line()}")
        self.console.print()

        if self.state.history:
            n = len(self.state.history)
            self.console.print(f"  [dim]↻ Resuming session ({n} messages)[/dim]")

        if not (self.root / ".simp").exists():
            self.console.print(
                "  [yellow]⚠  Project not initialized. Run[/yellow] [cyan]/init[/cyan] [yellow]to start.[/yellow]"
            )

        self.console.print(
            "  [dim]Type[/dim] [cyan]/help[/cyan] [dim]for commands · Tab for completions · Ctrl+C to interrupt[/dim]"
        )
        self.console.print()

    # ── main loop ──────────────────────────────────────────────────────────

    def run(self):
        self.welcome()

        while True:
            try:
                user_input = self.session.prompt(
                    [("class:prompt", "❯ ")],
                    auto_suggest=AutoSuggestFromHistory(),
                ).strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    self._route_command(user_input)
                else:
                    self._handle_chat(user_input)

            except KeyboardInterrupt:
                self.console.print("\n[dim]^C — type /exit to quit[/dim]")
                continue
            except EOFError:
                self._save_and_exit()
                break
            except Exception as e:
                self.console.print(f"\n[bold red]Error:[/bold red] {e}")

    def _save_and_exit(self):
        self.session_manager.save_session(self.state)
        self.console.print("\n[green]✓ Session saved. Goodbye![/green]\n")

    # ── command router ─────────────────────────────────────────────────────

    def _route_command(self, user_input: str):
        cmd_parts = user_input[1:].split(None, 1)
        cmd = cmd_parts[0].lower()
        args = cmd_parts[1] if len(cmd_parts) > 1 else ""

        if cmd in ("exit", "quit", "q"):
            self._save_and_exit()
            sys.exit(0)

        handlers = {
            "ask": self._cmd_ask,
            "do": self._cmd_do,
            "sync": self._cmd_sync,
            "status": self._cmd_status,
            "recover": self._cmd_recover,
            "init": self._cmd_init,
            "wiki": self._cmd_wiki,
            "config": self._cmd_config,
            "sessions": self._cmd_sessions,
            "simp": self._cmd_simp,
            "clear": self._cmd_clear,
            "help": self._cmd_help,
        }

        handler = handlers.get(cmd)
        if handler:
            handler(args)
        else:
            suggestions = [c for c in COMMANDS if c.startswith(cmd)]
            if suggestions:
                hint = ", ".join(f"[cyan]/{s}[/cyan]" for s in suggestions[:5])
                self.console.print(f"[red]Unknown:[/red] /{cmd}  → Did you mean {hint}?")
            else:
                self.console.print(f"[red]Unknown command:[/red] /{cmd}  — type [cyan]/help[/cyan]")

    # ── command handlers ───────────────────────────────────────────────────

    def _cmd_ask(self, args: str):
        if not args:
            self.console.print("[red]Usage:[/red] /ask <query>")
            return
        self.workflows.ask(
            args,
            provider=self.state.current_provider,
            model=self.state.current_model,
        )

    def _cmd_do(self, args: str):
        try:
            parts = shlex.split(args) if args else []
        except ValueError:
            self.console.print("[red]Error parsing command arguments.[/red]")
            return

        task_parts, yes, dry_run = [], False, False
        for part in parts:
            if part == "--yes":
                yes = True
            elif part == "--dry-run":
                dry_run = True
            else:
                task_parts.append(part)

        task = " ".join(task_parts)
        if not task:
            self.console.print("[red]Usage:[/red] /do <task> [--yes] [--dry-run]")
            return

        self.workflows.do(
            task,
            yes=yes,
            dry_run=dry_run,
            provider=self.state.current_provider,
            approval_prompt=self.session.prompt,
            model=self.state.current_model,
            session_manager=self.session_manager,
            session_state=self.state,
        )

    def _cmd_sync(self, args: str):
        self.workflows.sync()

    def _cmd_status(self, args: str):
        self.workflows.status()

    def _cmd_recover(self, args: str):
        self.workflows.recover(approval_prompt=self.session.prompt)

    def _cmd_init(self, args: str):
        with self.console.status("[cyan]Initializing project…[/cyan]"):
            self.workflows.init_project(
                provider=self.state.current_provider,
                model=self.state.current_model,
            )
        self.console.print("[green]✓ Project initialized[/green]")

    def _cmd_simp(self, args: str):
        try:
            parts = shlex.split(args) if args else []
        except ValueError:
            self.console.print("[red]Error parsing arguments.[/red]")
            return

        simp_path = self.root / "SIMP.md"

        if not parts or parts[0] == "show":
            if simp_path.exists():
                self.console.print(Panel(simp_path.read_text(), title="SIMP.md", border_style="magenta"))
            else:
                self.console.print("[yellow]SIMP.md not found.[/yellow]")
            return

        if parts[0] == "update":
            instruction = " ".join(parts[1:]).strip()
            if not instruction:
                self.console.print("[red]Usage:[/red] /simp update <instruction>")
                return
            self.workflows.update_simp(
                instruction,
                provider=self.state.current_provider,
                model=self.state.current_model,
                approval_prompt=self.session.prompt,
            )
            return

        self.console.print("[dim]Usage: /simp show | /simp update <instruction>[/dim]")

    def _cmd_wiki(self, args: str):
        try:
            parts = shlex.split(args) if args else []
        except ValueError:
            self.console.print("[red]Error parsing arguments.[/red]")
            return

        if not parts or parts[0] == "list":
            self.workflows.wiki_list()
            return

        if parts[0] == "show":
            if len(parts) < 2:
                self.console.print("[red]Usage:[/red] /wiki show <page-id>")
                return
            self.workflows.wiki_show(parts[1])
            return

        if parts[0] == "search":
            if len(parts) < 2:
                self.console.print("[red]Usage:[/red] /wiki search <keyword>")
                return
            self.console.print("[dim]Wiki search coming soon.[/dim]")
            return

        self.console.print("[dim]Usage: /wiki list | show <page> | search <keyword>[/dim]")

    def _cmd_config(self, args: str):
        try:
            parts = shlex.split(args) if args else []
        except ValueError:
            self.console.print("[red]Error parsing arguments.[/red]")
            return

        if not parts:
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column(style="dim", width=10)
            table.add_column(style="cyan")
            table.add_row("Provider", self.state.current_provider)
            table.add_row("Model", self.state.current_model)
            table.add_row("Session", self.state.session_id)
            table.add_row("Project", str(self.root))
            self.console.print(table)
            return

        if parts[0] == "--provider" and len(parts) > 1:
            self.state.current_provider = parts[1]
            self._refresh_llm()
            self.session_manager.save_session(self.state)
            self.console.print(f"[green]✓ Provider → {parts[1]}[/green]")
            return

        if parts[0] == "--model" and len(parts) > 1:
            self.state.current_model = " ".join(parts[1:])
            self._refresh_llm()
            self.session_manager.save_session(self.state)
            self.console.print(f"[green]✓ Model → {self.state.current_model}[/green]")
            return

        self.console.print("[dim]Usage: /config | --provider NAME | --model NAME[/dim]")

    def _cmd_sessions(self, args: str):
        try:
            parts = shlex.split(args) if args else []
        except ValueError:
            self.console.print("[red]Error parsing arguments.[/red]")
            return

        sessions = self.session_manager.list_sessions()
        if not sessions:
            self.console.print("[yellow]No sessions found.[/yellow]")
            return

        if not parts or parts[0] == "list":
            table = Table(title="Sessions", show_header=True, padding=(0, 1))
            table.add_column("ID", style="cyan", max_width=18)
            table.add_column("Updated", style="dim")
            table.add_column("Preview", style="dim", max_width=40)
            for s in sessions[:10]:
                table.add_row(s["id"][:16], time.ctime(s["last_updated"]), s["preview"][:40])
            self.console.print(table)
            return

        if parts[0] == "--switch" and len(parts) > 1:
            loaded = self.session_manager.load_session(parts[1])
            if loaded:
                self.state = loaded
                self._refresh_llm()
                self.console.print(f"[green]✓ Switched to {parts[1]}[/green]")
            else:
                self.console.print(f"[red]Session not found: {parts[1]}[/red]")
            return

        self.console.print("[dim]Usage: /sessions | --switch ID[/dim]")

    def _cmd_clear(self, args: str):
        self.state.history = []
        self.session_manager.save_session(self.state)
        self.console.print("[dim]✓ History cleared[/dim]")

    def _cmd_help(self, args: str):
        if args:
            cmd = args.lstrip("/").lower()
            desc = COMMANDS.get(cmd)
            if desc:
                self.console.print(f"  [cyan]/{cmd}[/cyan]  {desc}")
            else:
                self.console.print(f"  [red]Unknown command: /{cmd}[/red]")
            return

        self.console.print()
        self.console.print("[bold cyan]SimpCode Commands[/bold cyan]")
        self.console.print()

        groups = {
            "Research & Execution": ["ask", "do", "recover"],
            "Wiki & Sync": ["wiki", "sync", "status"],
            "Project": ["init", "simp", "config"],
            "Session": ["sessions", "clear"],
            "Other": ["help", "exit"],
        }

        for group_name, cmds in groups.items():
            self.console.print(f"  [bold yellow]{group_name}[/bold yellow]")
            for cmd in cmds:
                desc = COMMANDS.get(cmd, "")
                pad = " " * (12 - len(cmd))
                self.console.print(f"    [cyan]/{cmd}[/cyan]{pad}{desc}")
            self.console.print()

        self.console.print("[dim]  Tab → completions · @ → files · # → wiki pages[/dim]")
        self.console.print()

    # ── chat handler ───────────────────────────────────────────────────────

    def _handle_chat(self, user_input: str):
        llm = self._refresh_llm()
        self.workflows.chat_turn(self.state, self.session_manager, llm, user_input)
