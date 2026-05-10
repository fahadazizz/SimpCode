from typing import List, Optional
from pydantic import BaseModel

class PlanStep(BaseModel):
    id: int
    target: str
    action: str
    rationale: str
    verification: str

class Plan(BaseModel):
    task_id: str
    steps: List[PlanStep]
    scope_exclusions: List[str]
    risk_level: str  # low, medium, high

class PlanGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def generate(self, task: str, context: str) -> Plan:
        system_instruction = """You are the SimpCode Architect. 
Your job is to produce a concrete, step-by-step implementation plan for the user's task.
Consider:
1. Invariants: What rules must not be broken?
2. Risks: What could go wrong in the affected areas?
3. Seams: Where is it safe to modify?

Output your plan as a JSON object matching the provided schema.
"""
        prompt = f"User Task: {task}\n\nAssembled Context:\n{context}"
        
        result = self.llm.structured_output(prompt, Plan, system_instruction)
        return Plan(**result)
