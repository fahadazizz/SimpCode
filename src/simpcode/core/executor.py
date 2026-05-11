from pathlib import Path
from typing import List, Dict, Any, Optional
import time
from simpcode.core.planner import Plan, PlanStep
from simpcode.harness.tools import ToolHarness
from simpcode.core.llm import LLMClient
from simpcode.core.state import ExecutionLogger
from pydantic import BaseModel
from simpcode.core.prompts import registry
from rich.console import Console

class ToolCall(BaseModel):
    tool: str
    args: Dict[str, Any]
    thought: str # Reasoning for this specific tool call
    complete: bool # Set to true ONLY after the Plan Step is verified

class TakeAction:
    """
    SimpCode Executor: Responsible for safe, verifiable implementation of the plan.
    Implements a multi-turn ReAct (Reason + Act) loop per Plan Step.
    Enforces 'Read-Before-Write' and 'Inline Verification' invariants.
    """
    def __init__(self, root: Path, llm: LLMClient, session_id: Optional[str] = None):
        self.root = root
        self.llm = llm
        self.session_id = session_id or f"sess_{int(time.time())}"
        self.logger = ExecutionLogger(self.session_id)
        self.console = Console()

    def execute(self, plan: Plan, context: str, scanner=None, task: str = None):
        allowed_files = list(set([step.target for step in plan.steps]))
        harness = ToolHarness(self.root, allowed_files)
        
        current_context = context
        execution_trace = ""
        
        for step in plan.steps:
            if scanner and task:
                self.console.print("[dim]Refreshing Context...[/dim]")
                try:
                    current_context = scanner.run(task)
                except Exception as e:
                    self.console.print(f"[yellow]Context refresh failed: {e}[/yellow]")
            self.console.print(f"\n[bold blue]>>> EXECUTION STEP {step.id}[/bold blue]: {step.action}")
            
            step_complete = False
            step_turns = 0
            max_step_turns = 30 # Increased for production readiness 
            
            while not step_complete and step_turns < max_step_turns:
                step_turns += 1
                
                system_instruction = registry.load("staff_implementer")
                
                try:
                    tool_call = self.llm.structured_output(
                        f"EXECUTION HISTORY:\n{execution_trace}\n\nCURRENT CONTEXT:\n{current_context}\n\nNext Action:",
                        ToolCall,
                        system_instruction
                    )
                except Exception as e:
                    self.console.print(f"  [bold red][!] Reasoning Failure:[/bold red] {e}")
                    break

                self.console.print(f"  [dim][Thought]:[/dim] {tool_call.thought}")
                
                if tool_call.complete:
                    self.console.print(f"  [bold green][✓] Step {step.id} verified and complete.[/bold green]")
                    step_complete = True
                    continue

                self.console.print(f"  [cyan][Action]:[/cyan] {tool_call.tool}({tool_call.args})")

                # Execute via Harness
                try:
                    result = ""
                    status = "success"
                    
                    if tool_call.tool == "read_file":
                        result = harness.read_file(tool_call.args["path"])
                    elif tool_call.tool in ["write_file", "patch_file"]:
                        file_path = tool_call.args["path"]
                        if tool_call.tool == "write_file":
                            harness.write_file(file_path, tool_call.args["content"])
                        else:
                            harness.patch_file(file_path, tool_call.args["old_string"], tool_call.args["new_string"])
                        
                        # System-enforced structural linting
                        lint_result = harness.run_shell(f"flake8 {file_path}")
                        if "EXECUTION FAILURE" in lint_result or "Security Error" in lint_result:
                            result = f"File updated, but structural linting failed. You MUST fix this error before proceeding:\n{lint_result}"
                            status = "failure"
                        else:
                            result = "File updated and passed structural linting. Proceed."
                    elif tool_call.tool == "run_shell":
                        result = harness.run_shell(tool_call.args["command"])
                        if "ERROR" in result or "FAILURE" in result:
                            status = "failure"
                    else:
                        result = f"Error: Unknown tool '{tool_call.tool}'"
                        status = "error"
                    
                    # Update state
                    self.logger.log_event(tool_call.tool, tool_call.args, result, status)
                    trace_entry = f"\nTurn {step_turns} (Step {step.id}): {tool_call.tool} -> {status}\nResult: {result[:1000]}..."
                    execution_trace += trace_entry
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"  [!] {error_msg}")
                    self.logger.log_event(tool_call.tool, tool_call.args, error_msg, "exception")
                    execution_trace += f"\nTurn {step_turns} (Step {step.id}): {tool_call.tool} -> EXCEPTION: {error_msg}"
                    
            if not step_complete:
                print(f"[red]CRITICAL: Step {step.id} failed after {max_step_turns} attempts. Aborting plan.[/red]")
                break
                
        return execution_trace
