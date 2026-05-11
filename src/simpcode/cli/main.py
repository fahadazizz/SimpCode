import click
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

# Production Readiness: Load environment early
load_dotenv()

from simpcode.core.paths import get_project_root, get_wiki_dir, get_plans_dir
from simpcode.core.analyzer import ProjectAnalyzer
from simpcode.core.generator import IntelligenceSynthesizer, DocumentGenerator
from simpcode.core.llm import LLMClient
from simpcode.core.modes import ScanScene
from simpcode.core.planner import PlanGenerator, Plan
from simpcode.core.executor import TakeAction
from simpcode.core.evolution import GetBetter
from simpcode.harness.permissions import PermissionSystem
from simpcode.wiki.engine import WikiEngine
from simpcode.wiki.bootstrap import WikiBootstrap
from simpcode.core.config import global_config, LLMProviderConfig, SimpConfig
from simpcode.core.prompts import registry

console = Console()

@click.group()
def cli():
    """SimpCode: High-Integrity Agentic Engineering Assistant."""
    pass

@cli.command()
def setup():
    """Configure global LLM provider and API keys."""
    console.print(Panel("SimpCode Global Setup", border_style="magenta"))
    
    provider = click.prompt(
        "Choose LLM Provider", 
        type=click.Choice(["groq", "anthropic", "openai", "openrouter", "google", "ollama"]),
        default=global_config.config.active_provider
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
        provider=provider,
        model_id=model_id,
        api_key=api_key,
        base_url=base_url
    )
    
    config = global_config.config
    config.active_provider = provider
    config.providers[provider] = new_provider_config
    
    global_config.save(config)
    console.print(f"\n[bold green]✓ Configuration saved to {global_config.config_path}[/bold green]")

@cli.command()
def init():
    """Get Mission: Onboard SimpCode to the current project."""
    root = get_project_root()
    console.print(Panel(f"Initializing SimpCode at [bold]{root}[/bold]", title="GET MISSION", border_style="blue"))
    
    llm = LLMClient()
    analyzer = ProjectAnalyzer(root)
    synthesizer = IntelligenceSynthesizer(llm)
    generator = DocumentGenerator(root)
    bootstrap = WikiBootstrap(llm, root)
    
    try:
        with console.status("[bold blue]Collecting codebase metadata..."):
            metadata = analyzer.collect_metadata()
        
        with console.status("[bold blue]Synthesizing Project Intelligence..."):
            docs = synthesizer.synthesize(metadata)
            generator.write_docs(docs)
            
        with console.status("[bold blue]Compiling Initial Wiki (Semantic Core)..."):
            bootstrap.run(metadata)
        
        console.print("\n[bold green]✓ Mission Establishment Complete.[/bold green]")
        console.print(" - [cyan]SIMP.md[/cyan] (Project Intelligence)")
        console.print(" - [cyan]AGENT.md[/cyan] (Behavioral Rules)")
        console.print(" - [cyan].simp/wiki/[/cyan] (Knowledge Base)")
        console.print("\nRun `simp status` to verify health.")
    except Exception as e:
        console.print(f"[bold red]Initialization Failed:[/bold red] {e}")

@cli.command()
@click.argument('question')
def ask(question):
    """Scan Scene: Query the codebase using Wiki context (Read-Only)."""
    root = get_project_root()
    llm = LLMClient()
    scanner = ScanScene(root, llm)
    
    try:
        with console.status("[bold blue]Scanning scene and navigating Wiki..."):
            context = scanner.run(question)
        
        with console.status("[bold blue]Reasoning..."):
            instruction = registry.load("research_assistant")
            response = llm.chat([{"role": "user", "content": f"CONTEXT:\n{context}\n\nQUERY: {question}"}], instruction)
        
        console.print(Panel(response, title="SimpCode Analysis", border_style="green"))
    except Exception as e:
        console.print(f"[bold red]Query Error:[/bold red] {e}")

@cli.command()
@click.argument('task')
@click.option('--yes', is_flag=True, help="Autonomous mode: Skip approval gate.")
@click.option('--dry-run', is_flag=True, help="Think Through only: Generate plan without execution.")
def do(task, yes, dry_run):
    """Full Lifecycle: Execute a task with reasoning, planning, and verification."""
    root = get_project_root()
    llm = LLMClient()
    scanner = ScanScene(root, llm)
    planner = PlanGenerator(llm, scanner)
    permissions = PermissionSystem(console)
    session_id = f"task_{int(time.time())}"
    executor = TakeAction(root, llm, session_id=session_id)
    evolver = GetBetter(root, llm)
    
    try:
        with console.status("[bold blue]Scanning impact surface..."):
            context = scanner.run(task)
        
        with console.status("[bold blue]Thinking Through (Planning)..."):
            plan = planner.generate(task, context)
            plan.task_id = session_id
            
        # Persist Plan Artifact
        plan_path = get_plans_dir() / f"plan_{session_id}.json"
        plan_path.write_text(plan.model_dump_json(indent=2))
        
        if dry_run:
            permissions.review_plan(plan)
            console.print("\n[yellow]Dry-run complete. No changes made.[/yellow]")
            return

        approved = yes or permissions.review_plan(plan)
        
        if approved:
            console.print("\n[bold green]Plan Approved. Transitioning to TAKE ACTION.[/bold green]")
            execution_trace = executor.execute(plan, context)
            
            with console.status("[bold blue]Getting Better (Reflecting)..."):
                proposals = evolver.run(task, execution_trace)
            
            if proposals:
                has_elements = proposals.new_patterns or proposals.new_risks or proposals.new_invariants
                if has_elements:
                    console.print("\n[bold magenta]Evolution Proposals Discovered[/bold magenta]")
                    if proposals.new_patterns:
                        console.print(f"[cyan]Patterns:[/cyan] {proposals.new_patterns}")
                    if proposals.new_risks:
                        console.print(f"[cyan]Risks:[/cyan] {proposals.new_risks}")
                    if proposals.new_invariants:
                        console.print(f"[cyan]Invariants:[/cyan] {proposals.new_invariants}")
                    
                    if click.confirm("\nDo you want to append these insights to the Wiki?"):
                        with console.status("Saving Evolution Insights..."):
                            evolver.append_proposals(proposals)
                            console.print("[green]✓ Insights integrated into the cognitive layers.[/green]")

            console.print("\n[bold green]✓ Task lifecycle complete.[/bold green]")
        else:
            console.print("\n[red]Task Aborted by User.[/red]")
    except Exception as e:
        console.print(f"[bold red]Execution Failure:[/bold red] {e}")

@cli.command()
def sync():
    """Get Better: Batch-verify Wiki freshness and regenerate stale pages."""
    root = get_project_root()
    wiki = WikiEngine(root)
    llm = LLMClient()
    
    console.print("[bold blue]Synchronizing Wiki with Source Truth...[/bold blue]")
    
    pages = wiki.get_all_pages()
    stale_count = 0
    
    for page in pages:
        stale_sources = wiki.check_staleness(page)
        if stale_sources:
            stale_count += 1
            console.print(f"Page [yellow]{page.metadata.id}[/yellow] is stale. Regenerating...")
            
            with console.status(f"Compiling {page.metadata.id}..."):
                code_context = ""
                for source, current_hash in stale_sources:
                    full_path = root / source.file_path
                    if full_path.exists():
                        code_context += f"--- {source.file_path} ---\n{full_path.read_text()[:5000]}\n"
                    source.hash = current_hash 
                
                instruction = registry.load("wiki_maintainer")
                prompt = f"OLD CONTENT:\n{page.content}\n\nCurrent Code:\n{code_context}\n\nUpdate page."
                
                page.content = llm.chat([{"role": "user", "content": prompt}], instruction)
                page.metadata.last_updated = time.time()
                wiki.save_page(page)
                console.print(f"  [green]✓[/green] Synchronized {page.metadata.id}")

    if stale_count == 0:
        console.print("[green]Wiki is consistent with codebase.[/green]")
    else:
        console.print(f"\n[bold green]Synchronization complete.[/bold green]")

@cli.command()
def status():
    """Check SimpCode health and Wiki integrity."""
    root = get_project_root()
    wiki = WikiEngine(root)
    
    console.print(Panel(f"Project: [bold]{root.name}[/bold]\nRoot: {root}", title="SIMPCODE STATUS", border_style="cyan"))
    
    pages = wiki.get_all_pages()
    stale_pages = [p for p in pages if wiki.is_page_stale(p)]
    
    table = Table(show_header=False, box=None)
    table.add_row("Wiki Pages:", f"{len(pages)}")
    table.add_row("Stale Pages:", f"[bold red]{len(stale_pages)}[/bold red]" if stale_pages else "[green]0[/green]")
    
    console.print(table)
    
    if stale_pages:
        console.print("\n[yellow]Stale Knowledge Detected:[/yellow]")
        for p in stale_pages:
            console.print(f"  - {p.metadata.id}")
        console.print("\nRun `simp sync` to restore consistency.")

@click.group()
def wiki():
    """Inspect and manage the Semantic Core (Wiki)."""
    pass

@wiki.command(name="show")
@click.argument('page_id')
def wiki_show(page_id):
    """Render a Wiki page."""
    root = get_project_root()
    wiki = WikiEngine(root)
    page = wiki.get_page(page_id)
    if page:
        console.print(Panel(page.content, title=f"WIKI: {page_id}", subtitle=f"Type: {page.metadata.type} | Last Updated: {time.ctime(page.metadata.last_updated)}"))
    else:
        console.print(f"[red]Error: Knowledge node '{page_id}' not found.[/red]")

@wiki.command(name="list")
def wiki_list():
    """List all knowledge nodes."""
    root = get_project_root()
    wiki = WikiEngine(root)
    pages = wiki.get_all_pages()
    
    table = Table(title="Knowledge Graph (Wiki)")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Freshness", justify="center")
    
    for p in pages:
        freshness = "[red]STALE[/red]" if wiki.is_page_stale(p) else "[green]FRESH[/green]"
        table.add_row(p.metadata.id, p.metadata.type, freshness)
    
    console.print(table)

@cli.command()
def recover():
    """Resilience: Restore or revert an interrupted session."""
    root = get_project_root()
    plans_dir = get_plans_dir()
    plans = list(plans_dir.glob("*.json"))
    
    if not plans:
        console.print("[yellow]No recoverable sessions found.[/yellow]")
        return
        
    latest_plan_file = max(plans, key=lambda p: p.stat().st_mtime)
    console.print(f"[bold blue]Recovery Mode:[/bold blue] Loading session {latest_plan_file.name}")
    
    import json
    from simpcode.core.planner import Plan
    plan_data = json.loads(latest_plan_file.read_text())
    plan = Plan(**plan_data)
    
    permissions = PermissionSystem(console)
    if permissions.review_plan(plan):
        llm = LLMClient()
        executor = TakeAction(root, llm, session_id=plan.task_id)
        executor.execute(plan, "RECOVERY CONTEXT: Session restored from persisted plan artifact.")
        console.print("[bold green]✓ Session Recovery Successful.[/bold green]")

from simpcode.cli.shell import SimpShell

@cli.command()
def chat():
    """Interactive TUI session mode."""
    shell = SimpShell()
    shell.run()

def main():
    # Register groups
    cli.add_command(wiki)
    cli()

if __name__ == "__main__":
    main()
