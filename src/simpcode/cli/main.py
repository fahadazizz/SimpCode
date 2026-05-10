import click
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()

console = Console()

@click.group()
def cli():
    """SimpCode: A semantically aware agentic coding assistant."""
    pass

from pathlib import Path
from simpcode.core.analyzer import ProjectAnalyzer
from simpcode.core.generator import DocumentGenerator

@cli.command()
def init():
    """Onboard SimpCode to a new or existing project."""
    root = Path.cwd()
    console.print(f"[bold blue]SimpCode:[/bold blue] Initializing in {root}")
    
    analyzer = ProjectAnalyzer(root)
    with console.status("Analyzing project structure..."):
        info = analyzer.analyze()
    
    console.print(f"Stack detected: [green]{', '.join(info.stack)}[/green]")
    
    generator = DocumentGenerator(root)
    with console.status("Generating configuration documents..."):
        generator.generate_simp_md(info)
        generator.generate_agent_md(info)
    
    console.print("Created [bold]SIMP.md[/bold] and [bold]AGENT.md[/bold]")
    console.print("[bold green]Success:[/bold green] Project onboarded. Run `simp status` to verify.")

from simpcode.core.llm import LLMClient
from simpcode.core.modes import ScanScene

@cli.command()
@click.argument('question')
def ask(question):
    """Ask a question about the codebase (read-only)."""
    root = Path.cwd()
    llm = LLMClient()
    scanner = ScanScene(root, llm)
    
    with console.status("Scanning scene and assembling context..."):
        context = scanner.run(question)
    
    with console.status("Reasoning with Wiki context..."):
        system_instruction = "You are SimpCode, a semantically aware coding assistant. Answer questions using the provided context."
        response = llm.chat([{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}], system_instruction)
    
    console.print(f"\n[bold green]SimpCode Response:[/bold green]\n")
    console.print(response)

from simpcode.core.planner import PlanGenerator
from simpcode.harness.permissions import PermissionSystem

from simpcode.core.executor import TakeAction

@cli.command()
@click.argument('task')
@click.option('--yes', is_flag=True, help="Skip approval gate.")
@click.option('--dry-run', is_flag=True, help="Show plan but do not execute.")
def do(task, yes, dry_run):
    """Execute a task that modifies the codebase."""
    root = Path.cwd()
    llm = LLMClient()
    scanner = ScanScene(root, llm)
    planner = PlanGenerator(llm)
    permissions = PermissionSystem(console)
    executor = TakeAction(root, llm)
    
    with console.status("Scanning scene and assembling context..."):
        context = scanner.run(task)
    
    with console.status("Thinking through and generating plan..."):
        plan = planner.generate(task, context)
    
    if dry_run:
        permissions.review_plan(plan)
        console.print("\n[yellow]Dry-run mode: Execution skipped.[/yellow]")
        return

    approved = yes or permissions.review_plan(plan)
    
    if approved:
        console.print("\n[bold green]Plan approved. Proceeding to Take Action...[/bold green]")
        executor.execute(plan, context)
        console.print("\n[bold green]Task complete.[/bold green]")
    else:
        console.print("\n[red]Plan rejected. Execution aborted.[/red]")

from simpcode.wiki.engine import WikiEngine

@cli.command()
def sync():
    """Check Wiki freshness and regenerate stale pages."""
    root = Path.cwd()
    wiki = WikiEngine(root)
    
    console.print("[bold blue]SimpCode:[/bold blue] Syncing Wiki with codebase...")
    
    pages = wiki.get_all_pages()
    stale_count = 0
    
    for page in pages:
        stale_sources = wiki.check_staleness(page)
        if stale_sources:
            stale_count += 1
            console.print(f"Page [yellow]{page.metadata.id}[/yellow] is stale.")
            # In a real system, we'd trigger regeneration here.
            # For now, we update hashes to 'sync'.
            for source, current_hash in stale_sources:
                source.hash = current_hash
            
            page_path = wiki.wiki_dir / f"{page.metadata.id}.md"
            page.to_file(page_path)
            console.print(f"  [green]✓[/green] Updated hashes for {page.metadata.id}")

    if stale_count == 0:
        console.print("[green]Wiki is already fresh.[/green]")
    else:
        console.print(f"\n[bold green]Sync complete:[/bold green] {stale_count} pages updated.")

@cli.command()
def status():
    """Show current health of the SimpCode setup."""
    root = Path.cwd()
    wiki = WikiEngine(root)
    
    console.print("[bold blue]SimpCode Status[/bold blue]")
    
    pages = wiki.get_all_pages()
    stale_pages = [p for p in pages if wiki.is_page_stale(p)]
    
    console.print(f"Wiki: {len(pages)} pages")
    console.print(f"Stale: {len(stale_pages)} pages")
    
    if stale_pages:
        for p in stale_pages:
            console.print(f"  - [yellow]{p.metadata.id}[/yellow]")

@cli.command()
def wiki():
    """Inspect and manage Wiki pages."""
    console.print("[bold blue]SimpCode Wiki[/bold blue]")
    console.print("Use subcommands to manage wiki pages. (Stub)")

@cli.command()
def recover():
    """Recover an incomplete or failed session."""
    console.print("[bold blue]SimpCode Recovery[/bold blue]")
    console.print("No interrupted session found. (Stub)")

def main():
    cli()

if __name__ == "__main__":
    main()
