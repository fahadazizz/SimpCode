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
from simpcode.harness.permissions import PermissionSystem
from simpcode.wiki.engine import WikiEngine
from simpcode.core.prompts import registry

class SimpShell:
    """
    SimpCode Interactive TUI: The primary interface for real-time engineering.
    Implements a full state machine from Mission to Reflection.
    """
    def __init__(self):
        self.console = Console()
        self.root = get_project_root()
        self.llm = LLMClient()
        self.session_id = f"shell_{int(time.time())}"
        
        # UI State
        self.history_path = Path.home() / ".simpcode" / "history"
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.session = PromptSession(history=FileHistory(str(self.history_path)))

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
        self.console.print(f"[dim]Provider: {self.llm.provider} ({self.llm.model_id})[/dim]\n")

    def run(self):
        self.welcome()
        
        # Check if project is initialized
        if not (self.root / ".simp").exists():
            self.console.print("[yellow]Warning: Project not initialized. Run `init` first or type 'init' here.[/yellow]")

        while True:
            try:
                user_input = self.session.prompt(
                    "simp> ",
                    auto_suggest=AutoSuggestFromHistory()
                ).strip()

                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                
                if user_input.lower() == "init":
                    self.console.print("[red]Please use `simp init` in a separate terminal.[/red]")
                    continue

                self.handle_task(user_input)

            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[bold red]Error:[/bold red] {e}")

    def handle_task(self, user_input: str):
        """
        Orchestrates the full Lifecycle for a given task input.
        """
        scanner = ScanScene(self.root, self.llm)
        
        # Determine if it's a 'question' or a 'do' task
        # For simplicity in the TUI, we treat everything as a collaborative chat first
        with self.console.status("[bold blue]Reasoning..."):
            context = scanner.run(user_input)
            instruction = registry.load("interactive_assistant")
            response = self.llm.chat([{"role": "user", "content": f"Context:\n{context}\n\nUser: {user_input}"}], instruction)
        
        self.console.print(f"\n[bold green]SimpCode:[/bold green] {response}\n")
