import shlex
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from simpcode.core.llm import LLMClient
from simpcode.core.paths import get_project_root
from simpcode.core.state import SessionManager, SessionMessage, SessionState
from simpcode.core.workflows import SimpWorkflows


class StatusBar:
    """Renders the status bar with project, session, and health info."""

    def __init__(self, root: Path, state: SessionState, wiki_health: Optional[str] = None):
        self.root = root
        self.state = state
        self.wiki_health = wiki_health or "Ready"

    def render(self) -> Panel:
        """Render status bar as a single-line panel."""
        status_items = [
            f"[cyan]Project:[/cyan] {self.root.name}",
            f"[magenta]Session:[/magenta] {self.state.session_id[:12]}...",
            f"[green]{self.state.current_provider}[/green] ({self.state.current_model[:20]}...)",
        ]

        health_color = "green" if self.wiki_health == "Ready" else "yellow"
        status_items.append(f"[{health_color}]✓ {self.wiki_health}[/{health_color}]")

        status_text = " │ ".join(status_items)
        return Panel(
            status_text,
            style="dim white on #1e1e1e",
            padding=(0, 1),
            expand=False,
        )


class CommandPalette:
    """Suggests available commands based on input."""

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

    @staticmethod
    def get_suggestions(prefix: str = "") -> List[str]:
        """Get command suggestions matching prefix."""
        if not prefix:
            return list(CommandPalette.COMMANDS.keys())

        prefix = prefix.lstrip("/").lower()
        return [
            cmd
            for cmd in CommandPalette.COMMANDS.keys()
            if cmd.startswith(prefix)
        ]

    @staticmethod
    def render_suggestions(suggestions: List[str]) -> str:
        """Format suggestions as a string."""
        if not suggestions:
            return ""
        cmds = ", ".join([f"[cyan]/{cmd}[/cyan]" for cmd in suggestions[:6]])
        return f"Suggestions: {cmds}"

    @staticmethod
    def get_help(command: str) -> str:
        """Get help text for a command."""
        cmd = command.lstrip("/").lower()
        return CommandPalette.COMMANDS.get(cmd, "Unknown command")


class TuiLayout:
    """Manages the rich layout zones for the TUI."""

    def __init__(self, console: Console):
        self.console = console

    def render_response_area(self, title: str, content: str) -> Panel:
        """Render response area with title."""
        return Panel(
            content,
            title=f"[bold cyan]{title}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )

    def render_command_reference(self) -> Panel:
        """Render quick command reference panel."""
        ref_table = Table(show_header=False, box=None, padding=(0, 1))
        ref_table.add_column(style="cyan", width=12)
        ref_table.add_column(style="dim")

        for cmd, desc in list(CommandPalette.COMMANDS.items())[:8]:
            ref_table.add_row(f"/{cmd}", desc)

        return Panel(
            ref_table,
            title="[bold]Commands[/bold]",
            border_style="blue",
            padding=(0, 1),
        )


class SimpShell:
    """
    SimpCode Interactive TUI: Gemini CLI-style interface for real-time engineering.
    All work happens in this interactive session with slash commands.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        self.console = Console()
        self.root = get_project_root()
        self.workflow = SimpWorkflows(self.console)

        # Session Management
        self.manager = SessionManager(str(self.root))
        if session_id:
            state = self.manager.load_session(session_id) or self._new_session(session_id)
        else:
            latest = self.manager.list_sessions()
            if latest:
                state = self.manager.load_session(latest[0]["id"]) or self._new_session()
            else:
                state = self._new_session()

        if provider:
            state.current_provider = provider
        if model_id:
            state.current_model = model_id

        self.state = state
        self.llm = self._refresh_llm()

        # UI Setup
        self.history_path = Path.home() / ".simpcode" / "history"
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

        # Create key bindings for shortcuts
        self.kb = KeyBindings()
        self._setup_key_bindings()

        self.session = PromptSession(
            history=FileHistory(str(self.history_path)),
            key_bindings=self.kb,
        )

        # Response display state
        self.last_response = None
        self.last_response_title = None
        self.show_command_ref = True

    def _setup_key_bindings(self):
        """Setup keyboard shortcuts."""
        @self.kb.add("c-h")
        def _(event):
            """Ctrl+H: Show command history."""
            self.console.print("\n[dim]Use arrow keys to navigate history[/dim]")

        @self.kb.add("c-l")
        def _(event):
            """Ctrl+L: Clear current input (handled by default)."""
            pass

        @self.kb.add("c-k")
        def _(event):
            """Ctrl+K: Toggle command palette."""
            self.show_command_ref = not self.show_command_ref

    def _new_session(self, session_id: Optional[str] = None) -> SessionState:
        """Create a new session."""
        sid = session_id or f"session_{int(time.time())}"
        state = SessionState(
            session_id=sid,
            project_root=str(self.root),
            current_provider=str(self.llm.provider_name) if hasattr(self, "llm") else "groq",
            current_model=str(self.llm.model_id) if hasattr(self, "llm") else "llama-3.3-70b-versatile",
        )
        self.manager.save_session(state)
        return state

    def _refresh_llm(self) -> LLMClient:
        """Rebuild the client from the current session state."""
        self.llm = LLMClient(
            provider=self.state.current_provider,
            model_id=self.state.current_model,
        )
        return self.llm

    def welcome(self):
        """Display welcome banner and status."""
        banner = r"""
   _____ _                 _____          _      
  / ____(_)               / ____|        | |     
 | (___  _ _ __ ___  _ __| |     ___   __| | ___ 
  \___ \| | '_ ` _ \| '_ \ |    / _ \ / _` |/ _ \
  ____) | | | | | | | |_) | |___| (_) | (_| |  __/
 |_____/|_|_| |_| |_| .__/ \_____\___/ \__,_|\___|
                    | |                           
                    |_|                           
[dim]TUI-First Agentic Engineering[/dim]
        """
        self.console.print(f"\n[bold blue]{banner}[/bold blue]")

        status_bar = StatusBar(self.root, self.state)
        self.console.print(status_bar.render())

        self.console.print(
            "\n[yellow]💡 Type[/yellow] [cyan]/help[/cyan] [yellow]for commands or start typing to chat[/yellow]\n"
        )

        if self.state.history:
            self.console.print(
                f"[dim]↻ Resuming session with {len(self.state.history)} messages[/dim]\n"
            )

        if not (self.root / ".simp").exists():
            self.console.print(
                "[yellow]⚠️  Project not initialized. Type[/yellow] [cyan]/init[/cyan] [yellow]to setup.[/yellow]\n"
            )

    def run(self):
        """Main TUI loop."""
        self.welcome()

        while True:
            try:
                # Get user input with better formatting
                user_input = self.session.prompt(
                    "\n[bold cyan]simp⟫[/bold cyan] ",
                    auto_suggest=AutoSuggestFromHistory(),
                ).strip()

                if not user_input:
                    continue

                # Route command or chat
                if user_input.startswith("/"):
                    self._route_command(user_input)
                else:
                    self._handle_chat(user_input)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]^C - Type[/yellow] [cyan]/exit[/cyan] [yellow]to quit[/yellow]")
                continue
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"\n[bold red]⚠️  Error:[/bold red] {e}")

    def _route_command(self, user_input: str):
        """Route slash commands to appropriate handlers."""
        cmd_parts = user_input[1:].split(None, 1)
        cmd = cmd_parts[0].lower()
        args = cmd_parts[1] if len(cmd_parts) > 1 else ""

        # Exit commands
        if cmd in ["exit", "quit", "q"]:
            self.manager.save_session(self.state)
            self.console.print(
                "\n[bold green]✓ Session saved. Goodbye![/bold green]\n"
            )
            sys.exit(0)

        # Main commands
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

        if cmd in handlers:
            handlers[cmd](args)
        else:
            suggestions = CommandPalette.get_suggestions(cmd)
            if suggestions:
                sugg_str = CommandPalette.render_suggestions(suggestions)
                self.console.print(f"[red]Unknown command:[/red] /{cmd}")
                self.console.print(sugg_str)
            else:
                self.console.print(f"[red]Unknown command:[/red] /{cmd}")
                self.console.print(CommandPalette.render_suggestions())

    def _cmd_ask(self, args: str):
        """Handle /ask command."""
        if not args:
            self.console.print("[red]✗ /ask requires a query[/red]")
            return

        with self.console.status("[cyan]⏳ Scanning scene and navigating Wiki...[/cyan]"):
            response = self.workflow.ask(
                args,
                provider=self.state.current_provider,
                model=self.state.current_model,
            )
        self.last_response = response
        self.last_response_title = "Analysis"

    def _cmd_do(self, args: str):
        """Handle /do command with flags."""
        try:
            parts = shlex.split(args) if args else []
        except:
            self.console.print("[red]✗ Error parsing command[/red]")
            return

        task_parts = []
        yes = False
        dry_run = False

        for part in parts:
            if part == "--yes":
                yes = True
            elif part == "--dry-run":
                dry_run = True
            else:
                task_parts.append(part)

        task = " ".join(task_parts)
        if not task:
            self.console.print("[red]✗ /do requires a task description[/red]")
            return

        with self.console.status("[cyan]⏳ Planning mission...[/cyan]"):
            self.workflow.do(
                task,
                yes=yes,
                dry_run=dry_run,
                provider=self.state.current_provider,
                approval_prompt=self.session.prompt,
                model=self.state.current_model,
            )

    def _cmd_sync(self, args: str):
        """Handle /sync command."""
        self.workflow.sync()

    def _cmd_status(self, args: str):
        """Handle /status command."""
        self.workflow.status()

    def _cmd_recover(self, args: str):
        """Handle /recover command."""
        self.workflow.recover(approval_prompt=self.session.prompt)

    def _cmd_simp(self, args: str):
        """Handle /simp command for SIMP.md inspection and updates."""
        try:
            parts = shlex.split(args) if args else []
        except:
            self.console.print("[red]✗ Error parsing command[/red]")
            return

        simp_path = self.root / "SIMP.md"

        if not parts or parts[0] == "show":
            if simp_path.exists():
                self.console.print(Panel(simp_path.read_text(), title="SIMP.md", border_style="magenta"))
            else:
                self.console.print("[yellow]SIMP.md does not exist yet.[/yellow]")
            return

        if parts[0] == "update":
            instruction = " ".join(parts[1:]).strip()
            if not instruction:
                self.console.print("[red]✗ Usage: /simp update <instruction>[/red]")
                return

            with self.console.status("[cyan]⏳ Updating SIMP.md...[/cyan]"):
                self.workflow.update_simp(
                    instruction,
                    provider=self.state.current_provider,
                    model=self.state.current_model,
                    approval_prompt=self.session.prompt,
                )
            return

        self.console.print("[yellow]Usage:[/yellow]")
        self.console.print("  /simp show                  Show current SIMP.md")
        self.console.print("  /simp update <instruction>  Update SIMP.md explicitly")

    def _cmd_init(self, args: str):
        """Handle /init command."""
        with self.console.status("[cyan]⏳ Initializing project...[/cyan]"):
            self.workflow.init_project(
                provider=self.state.current_provider,
                model=self.state.current_model,
            )
        self.console.print("[bold green]✓ Project initialized[/bold green]")

    def _cmd_wiki(self, args: str):
        """Handle /wiki command."""
        try:
            parts = shlex.split(args) if args else []
        except:
            self.console.print("[red]✗ Error parsing command[/red]")
            return

        if not parts or parts[0] == "list":
            self.workflow.wiki_list()
            return

        if parts[0] == "show":
            if len(parts) < 2:
                self.console.print("[red]✗ Usage: /wiki show <page-id>[/red]")
                return
            self.workflow.wiki_show(parts[1])
            return

        if parts[0] == "search":
            if len(parts) < 2:
                self.console.print("[red]✗ Usage: /wiki search <keyword>[/red]")
                return
            self.console.print("[yellow]⏳ Searching wiki...[/yellow]")
            self.console.print("[dim]Wiki search coming soon[/dim]")
            return

        self.console.print("[red]✗ Usage: /wiki list | show <page> | search <keyword>[/red]")

    def _cmd_config(self, args: str):
        """Handle /config command."""
        try:
            parts = shlex.split(args) if args else []
        except:
            self.console.print("[red]✗ Error parsing command[/red]")
            return

        if not parts:
            # Show current config
            table = Table(title="Current Configuration", show_header=False, box=None)
            table.add_row("Provider:", f"[cyan]{self.state.current_provider}[/cyan]")
            table.add_row("Model:", f"[cyan]{self.state.current_model}[/cyan]")
            table.add_row("Session:", f"[cyan]{self.state.session_id}[/cyan]")
            table.add_row("Project:", f"[cyan]{self.root}[/cyan]")
            self.console.print(table)
            return

        if parts[0] == "--provider" and len(parts) > 1:
            self.state.current_provider = parts[1]
            self._refresh_llm()
            self.manager.save_session(self.state)
            self.console.print(f"[bold green]✓ Provider set to {parts[1]}[/bold green]")
            return

        if parts[0] == "--model" and len(parts) > 1:
            self.state.current_model = " ".join(parts[1:])
            self._refresh_llm()
            self.manager.save_session(self.state)
            self.console.print(
                f"[bold green]✓ Model set to {self.state.current_model}[/bold green]"
            )
            return

        self.console.print("[yellow]Usage:[/yellow]")
        self.console.print("  /config                  Show current settings")
        self.console.print("  /config --provider NAME  Change LLM provider")
        self.console.print("  /config --model NAME     Change model ID")

    def _cmd_sessions(self, args: str):
        """Handle /sessions command."""
        try:
            parts = shlex.split(args) if args else []
        except:
            self.console.print("[red]✗ Error parsing command[/red]")
            return

        sessions = self.manager.list_sessions()

        if not sessions:
            self.console.print("[yellow]No sessions found[/yellow]")
            return

        if not parts or parts[0] == "list":
            table = Table(title="Recent Sessions", show_header=True)
            table.add_column("Session ID", style="cyan")
            table.add_column("Last Updated", style="magenta")
            table.add_column("Preview", style="dim", width=40)

            for s in sessions[:10]:
                table.add_row(
                    s["id"][:16],
                    time.ctime(s["last_updated"]),
                    s["preview"][:40],
                )
            self.console.print(table)
            return

        if parts[0] == "--switch" and len(parts) > 1:
            session_id = parts[1]
            loaded = self.manager.load_session(session_id)
            if loaded:
                self.state = loaded
                self._refresh_llm()
                self.console.print(
                    f"[bold green]✓ Switched to session {session_id}[/bold green]"
                )
            else:
                self.console.print(f"[red]✗ Session not found: {session_id}[/red]")
            return

        self.console.print("[yellow]Usage:[/yellow]")
        self.console.print("  /sessions                Show recent sessions")
        self.console.print("  /sessions --switch ID    Load different session")

    def _cmd_clear(self, args: str):
        """Handle /clear command."""
        try:
            parts = shlex.split(args) if args else []
        except:
            self.console.print("[red]✗ Error parsing command[/red]")
            return

        if not parts or parts[0] != "--full":
            self.state.history = []
            self.manager.save_session(self.state)
            self.console.print("[dim]✓ Chat history cleared[/dim]")
        else:
            self.state.history = []
            self.manager.save_session(self.state)
            self.console.print(
                "[dim]✓ Chat history and cache cleared[/dim]"
            )

    def _cmd_help(self, args: str):
        """Handle /help command."""
        if args:
            try:
                cmd = args.lstrip("/").lower()
                help_text = CommandPalette.get_help(cmd)
                self.console.print(f"[cyan]/{cmd}[/cyan]: {help_text}")
            except:
                self.console.print(f"[red]✗ Unknown command: /{args}[/red]")
            return

        # Show full help
        help_text = """[bold cyan]SimpCode Commands[/bold cyan]

[bold yellow]Research & Analysis:[/bold yellow]
  /ask <query>                    Research codebase using Wiki

[bold yellow]Task Execution:[/bold yellow]
  /do <task> [--yes] [--dry-run]  Plan and execute tasks
  /recover                        Restore latest plan

[bold yellow]Wiki Management:[/bold yellow]
  /wiki list                      Show all pages
  /wiki show <page-id>            Render a page
  /wiki search <keyword>          Search pages
  /sync                           Sync wiki with code

[bold yellow]Project Management:[/bold yellow]
  /status                         Show health
  /init                           Onboard project
  /config [--provider|--model]    LLM settings

[bold yellow]Session Management:[/bold yellow]
  /sessions [--switch ID]         Manage sessions
  /clear [--full]                 Clear history

[bold yellow]Utilities:[/bold yellow]
  /help [command]                 This help
  /exit                           Save and quit

[dim]Tips: Type Ctrl+K to toggle command palette, arrow keys for history[/dim]"""

        self.console.print(help_text)

    def _handle_chat(self, user_input: str):
        """Handle regular chat input (not a command)."""
        self._refresh_llm()
        self.workflow.chat_turn(self.state, self.manager, self.llm, user_input)
