from pathlib import Path
from typing import List
from simpcode.core.planner import Plan, PlanStep
from simpcode.harness.tools import ToolHarness
from simpcode.core.llm import LLMClient

class TakeAction:
    def __init__(self, root: Path, llm: LLMClient):
        self.root = root
        self.llm = llm

    def execute(self, plan: Plan, context: str):
        # Extract allowed files from plan targets
        allowed_files = list(set([step.target for step in plan.steps]))
        harness = ToolHarness(self.root, allowed_files)
        
        current_context = context
        
        for step in plan.steps:
            print(f"\n[bold blue]Step {step.id}:[/bold blue] {step.action} on {step.target}")
            
            # 1. Reason about the specific tool calls for this step
            # This is a "Mini-Step" logic
            tool_call_instruction = f"""You are executing Step {step.id} of an approved plan.
Step: {step.action} on {step.target}
Plan Rationale: {step.rationale}

Available Tools:
- read_file(path)
- write_file(path, content)
- run_shell(command)

Output your next tool call as a JSON object: {{"tool": "name", "args": {{"arg1": "val1"}}}}
"""
            # In a real system, this would loop until the step is complete.
            # For Phase 5, we implement a single-pass tool call to demonstrate the harness.
            
            tool_call = self.llm.structured_output(
                f"Current Context:\n{current_context}\n\nExecute the current step.",
                None, # Schema would be ToolCall model
                tool_call_instruction
            )
            
            # 2. Execute via Harness
            try:
                result = ""
                if tool_call["tool"] == "read_file":
                    result = harness.read_file(tool_call["args"]["path"])
                elif tool_call["tool"] == "write_file":
                    harness.write_file(tool_call["args"]["path"], tool_call["args"]["content"])
                    result = "File written successfully."
                elif tool_call["tool"] == "run_shell":
                    result = harness.run_shell(tool_call["args"]["command"])
                
                print(f"Tool Result: {result[:50]}...")
                current_context += f"\n\n--- Step {step.id} Result ---\n{result}"
                
            except Exception as e:
                print(f"[red]Error during step execution: {e}[/red]")
                break
