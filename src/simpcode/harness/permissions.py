from rich.table import Table
from rich.panel import Panel
from simpcode.core.planner import Plan

class PermissionSystem:
    def __init__(self, console):
        self.console = console

    def review_plan(self, plan: Plan) -> bool:
        self.console.print("\n[bold blue]─── Proposed Plan ───[/bold blue]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Step", style="dim", width=6)
        table.add_column("Target", width=20)
        table.add_column("Action")
        
        for step in plan.steps:
            table.add_row(str(step.id), step.target, step.action)
            
        self.console.print(table)
        
        if plan.scope_exclusions:
            self.console.print(f"\n[bold yellow]Scope Exclusions:[/bold yellow] {', '.join(plan.scope_exclusions)}")
            
        risk_color = "green" if plan.risk_level == "low" else "yellow" if plan.risk_level == "medium" else "red"
        self.console.print(f"\n[bold]Risk Level:[/bold] [{risk_color}]{plan.risk_level.upper()}[/{risk_color}]")
        
        confirm = input("\nDo you approve this plan? (y/n): ")
        return confirm.lower() == 'y'
