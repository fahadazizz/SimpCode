from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from simpcode.core.prompts import registry
from rich.console import Console

class PlanStep(BaseModel):
    id: int
    target: str
    action: str
    rationale: str
    verification: str # Command or criteria to verify this step

class Plan(BaseModel):
    task_id: str
    rationale: str # Overall architectural reasoning
    steps: List[PlanStep]
    scope_exclusions: List[str]
    risk_level: str  # low, medium, high

class ContextRequest(BaseModel):
    pages_to_load: List[str]
    rationale: str

class ArchitectResponse(BaseModel):
    is_plan: bool
    plan: Optional[Plan] = None
    request: Optional[ContextRequest] = None

class PlanGenerator:
    """
    SimpCode Architect: Responsible for high-integrity implementation planning.
    Follows CSIO (Context, Scope, Intent, Output) framework.
    """
    def __init__(self, llm_client, scanner):
        self.llm = llm_client
        self.scanner = scanner
        self.console = Console()

    def generate(self, task: str, initial_context: str) -> Plan:
        system_instruction = registry.load("staff_architect")
        current_context = initial_context

        # If a SPEC.md exists in the project, include it prominently in context
        try:
            spec_path = Path(self.scanner.root) / "SPEC.md"
            if spec_path.exists():
                spec_text = spec_path.read_text().strip()
                current_context = f"SPEC:\n{spec_text}\n\n" + current_context
        except Exception:
            pass


        max_turns = 3
        for turn in range(max_turns):
            prompt = registry.load("staff_architect_plan", include_base=False).format(
                current_context=current_context,
                task=task,
                mode_instruction=(
                    "You can either generate a production-grade Plan artifact (set is_plan=True and populate plan) "
                    "OR request more context if you lack information (set is_plan=False and populate request). "
                    "Ensure steps are atomic and verification is concrete."
                ),
            )
            response = self.llm.structured_output(prompt, ArchitectResponse, system_instruction)
            
            if response.is_plan and response.plan:
                return response.plan
            elif response.request:
                self.console.print(f"  [dim][Planner][/dim] Insufficient context. Requesting additional pages: {', '.join(response.request.pages_to_load)}")
                # Recursively fetch requested pages and build context
                for page_id in response.request.pages_to_load:
                    if page_id not in current_context:
                        page = self.scanner.wiki.get_page(page_id)
                        if page and not self.scanner.wiki.is_page_stale(page):
                            current_context += f"\n\n--- SUPPLEMENTAL CONTEXT: {page_id} ---\n{page.content}"
            else:
                self.console.print("  [dim][Planner][/dim] Invalid response. Proceeding to force plan generation.")
                break
                
        # Force plan on last turn if loop is exhausted
        prompt = registry.load("staff_architect_plan", include_base=False).format(
            current_context=current_context,
            task=task,
            mode_instruction="You MUST generate a final production-grade Plan artifact now (set is_plan=True and populate plan).",
        )
        response = self.llm.structured_output(prompt, ArchitectResponse, system_instruction)
        if response.plan:
            return response.plan
        raise RuntimeError("Planner failed to generate a valid plan.")
