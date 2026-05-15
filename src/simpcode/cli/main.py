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


@click.group(invoke_without_command=True)
@click.option("--provider", help="Override global LLM provider.")
@click.option("--model", help="Override global LLM model ID.")
@click.option("--session", help="Load a specific session ID.")
@click.option("--new", is_flag=True, help="Force a new session.")
@click.pass_context
def cli(ctx, provider, model, session, new):
    """SimpCode: High-Integrity Agentic Engineering Assistant.

    Run without arguments to enter the interactive TUI.
    """
    if ctx.invoked_subcommand is None:
        if new:
            session = f"session_{int(time.time())}"
        try:
            shell = SimpShell(provider=provider, model=model, session_id=session)
            shell.run()
        except Exception as e:
            console.print(f"[bold red]Launch failed:[/bold red] {e}")


@cli.command()
def setup():
    """Configure global LLM provider and API keys (one-time)."""
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
    console.print(f"[dim]Initializing at {root}…[/dim]")

    try:
        shell = SimpShell()
        shell.run()
    except Exception as e:
        console.print(f"[bold red]Initialization failed:[/bold red] {e}")


def _get_shell(ctx) -> SimpShell:
    provider = ctx.parent.params.get("provider") if ctx.parent else None
    model = ctx.parent.params.get("model") if ctx.parent else None
    session = ctx.parent.params.get("session") if ctx.parent else None
    return SimpShell(provider=provider, model=model, session_id=session)


@cli.command()
@click.argument("query", nargs=-1)
@click.pass_context
def ask(ctx, query):
    """Ask a question about the codebase without making changes."""
    query_str = " ".join(query)
    _get_shell(ctx)._cmd_ask(query_str)


@cli.command()
@click.argument("task", nargs=-1)
@click.option("--yes", is_flag=True, help="Auto-approve plan")
@click.option("--dry-run", is_flag=True, help="Plan only, no execution")
@click.pass_context
def do(ctx, task, yes, dry_run):
    """Execute a task."""
    task_str = " ".join(task)
    args = task_str
    if yes: args += " --yes"
    if dry_run: args += " --dry-run"
    _get_shell(ctx)._cmd_do(args.strip())


@cli.command()
@click.pass_context
def sync(ctx):
    """Force wiki synchronization."""
    _get_shell(ctx)._cmd_sync("")


@cli.command()
@click.pass_context
def status(ctx):
    """Show project status."""
    _get_shell(ctx)._cmd_status("")


@cli.command()
@click.argument("args", nargs=-1)
@click.pass_context
def wiki(ctx, args):
    """Manage or query the project Wiki."""
    _get_shell(ctx)._cmd_wiki(" ".join(args))


@cli.command()
@click.pass_context
def recover(ctx):
    """Recover from a broken state or failed execution."""
    _get_shell(ctx)._cmd_recover("")


def main():
    cli()


if __name__ == "__main__":
    main()
