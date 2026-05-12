import click
import time
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

# Production Readiness: Load environment early
load_dotenv()

from simpcode.core.config import global_config, LLMProviderConfig
from simpcode.core.paths import get_project_root
from simpcode.cli.shell import SimpShell

console = Console()


@click.group()
def cli():
    """SimpCode: High-Integrity Agentic Engineering Assistant."""
    pass


@cli.command()
def setup():
    """Configure global LLM provider and API keys (one-time, global setup)."""
    console.print(Panel("SimpCode Global Setup", border_style="magenta"))

    provider = click.prompt(
        "Choose LLM Provider",
        type=click.Choice(["groq", "anthropic", "openai", "openrouter", "google", "ollama"]),
        default=global_config.config.active_provider,
    )

    model_id = click.prompt("Enter Model ID", default="llama-3.3-70b-versatile")

    api_key = ""
    if provider != "ollama":
        api_key = click.prompt("Enter API Key", hide_input=True)

    base_url = None
    if provider == "ollama":
        base_url = click.prompt("Enter Ollama Base URL", default="http://localhost:11434/v1")

    # Update config
    new_provider_config = LLMProviderConfig(
        provider=provider, model_id=model_id, api_key=api_key, base_url=base_url
    )

    config = global_config.config
    config.active_provider = provider
    config.providers[provider] = new_provider_config

    global_config.save(config)
    console.print(
        f"\n[bold green]✓ Configuration saved to {global_config.config_path}[/bold green]"
    )


@cli.command()
def init():
    """Initialize SimpCode on the current project and enter TUI."""
    root = get_project_root()
    console.print(
        Panel(
            f"Initializing SimpCode at [bold]{root}[/bold]",
            title="GET MISSION",
            border_style="blue",
        )
    )

    try:
        shell = SimpShell()
        # Will auto-init inside shell if needed
        shell.run()
    except Exception as e:
        console.print(f"[bold red]Initialization Failed:[/bold red] {e}")


@cli.command()
@click.option("--provider", help="Override global LLM provider.")
@click.option("--model", help="Override global LLM model ID.")
@click.option("--session", help="Load a specific session ID.")
@click.option("--new", is_flag=True, help="Force a new session.")
def chat(provider, model, session, new):
    """Enter interactive TUI session (where all work happens)."""
    root = get_project_root()

    if new:
        session = f"session_{int(time.time())}"

    shell = SimpShell(provider=provider, model_id=model, session_id=session)
    shell.run()


@cli.command()
def help():
    """Show SimpCode help and command reference."""
    console.print(
        Panel(
            "SimpCode: TUI-First Agentic Engineering Assistant",
            border_style="cyan",
            title="ℹ️  Help",
        )
    )

    console.print("\n[bold cyan]Quick Start:[/bold cyan]")
    console.print("  [cyan]simp init[/cyan]       Initialize a project and enter TUI")
    console.print("  [cyan]simp chat[/cyan]       Enter interactive session")
    console.print("  [cyan]simp setup[/cyan]      Configure LLM provider (global, one-time)")

    console.print("\n[bold cyan]Interactive Commands (in TUI):[/bold cyan]")
    console.print("  Type [cyan]/help[/cyan] inside TUI for full command reference")
    console.print("  All work happens in the interactive session:")
    console.print("    • /ask <query>             - Research the codebase")
    console.print("    • /do <task> [--yes]       - Plan and execute tasks")
    console.print("    • /sync                    - Synchronize wiki with code")
    console.print("    • /status                  - Show project health")
    console.print("    • /wiki list|show|search   - Browse knowledge base")
    console.print("    • /sessions                - Manage sessions")
    console.print("    • /config                  - LLM configuration")

    console.print(
        "\n[dim]Note: SimpCode is TUI-first. All engineering work happens in the interactive session.[/dim]"
    )


def main():
    cli()


if __name__ == "__main__":
    main()
