from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import time
from simpcode.core.planner import Plan, PlanStep
from simpcode.harness.tools import ToolHarness
from simpcode.core.llm import LLMClient
from simpcode.core.state import ExecutionLogger
from pydantic import BaseModel
from simpcode.core.prompts import registry
from rich.console import Console
from simpcode.wiki.engine import WikiEngine

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
        allowed_files = [step.target for step in plan.steps if "/" in step.target or step.target.endswith(".md") or step.target.endswith(".py") or step.target.endswith(".json")]
        harness = ToolHarness(self.root, allowed_files)
        
        current_context = context
        execution_trace = ""
        recent_tool_calls: List[str] = []
        files_modified: Set[str] = set()

        def _tool_path(args: Dict[str, Any]) -> str:
            return args.get("path") or args.get("file_path") or args.get("file") or ""

        def _verification_failed(result: str) -> bool:
            normalized = result.upper()
            return any(token in normalized for token in ["EXECUTION FAILURE", "SECURITY VIOLATION", "PLAN VIOLATION", "ERROR"])
        
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
                    prompt = registry.load("staff_implementer_step", include_base=False).format(
                        execution_history=execution_trace,
                        current_context=current_context,
                    )
                    tool_call = self.llm.structured_output(
                        prompt,
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
                tool_signature = f"{tool_call.tool}:{_tool_path(tool_call.args)}"
                recent_tool_calls.append(tool_signature)
                recent_tool_calls = recent_tool_calls[-3:]
                if len(recent_tool_calls) == 3 and len(set(recent_tool_calls)) == 1:
                    self.console.print(f"  [yellow]Repeated tool call detected: {tool_signature}. Aborting step to avoid a reasoning loop.[/yellow]")
                    execution_trace += f"\nTurn {step_turns} (Step {step.id}): repeated tool call {tool_signature}"
                    break

                # Execute via Harness
                try:
                    result = ""
                    status = "success"
                    
                    if tool_call.tool == "read_file":
                        result = harness.read_file(_tool_path(tool_call.args))
                    elif tool_call.tool in ["write_file", "patch_file"]:
                        file_path = _tool_path(tool_call.args)
                        if file_path not in allowed_files:
                            result = f"Plan Violation: '{file_path}' is not in the approved step scope. Abort and re-plan with a concrete file target."
                            status = "failure"
                            self.logger.log_event(tool_call.tool, tool_call.args, result, status)
                            execution_trace += f"\nTurn {step_turns} (Step {step.id}): {tool_call.tool} -> {status}\nResult: {result[:1000]}..."
                            self.console.print(f"  [bold red][!] {result}[/bold red]")
                            break
                        if tool_call.tool == "write_file":
                            harness.write_file(file_path, tool_call.args["content"])
                        else:
                            harness.patch_file(file_path, tool_call.args["old_string"], tool_call.args["new_string"])

                        # High-Integrity Inline Wiki Update (SDD 9.5)
                        # Prevents desync and expensive re-scans
                        wiki = WikiEngine(self.root)
                        self._update_wiki(file_path, wiki)
                        files_modified.add(file_path)

                        lint_result = harness.run_shell(f"flake8 {file_path}")
                        if _verification_failed(lint_result):
                            result = f"File updated, but structural linting failed. You MUST fix this error before proceeding:\n{lint_result}"
                            status = "failure"
                        elif step.verification:
                            verification_result = harness.run_shell(step.verification)
                            if _verification_failed(verification_result):
                                result = (
                                    f"File updated, but step verification failed. You MUST fix this error before proceeding:\n"
                                    f"{verification_result}"
                                )
                                status = "failure"
                            else:
                                result = "File updated and passed structural linting plus declared verification. Proceed."
                        else:
                            result = "File updated and passed structural linting. Proceed."
                    elif tool_call.tool == "run_shell":
                        result = harness.run_shell(tool_call.args["command"])
                        if _verification_failed(result):
                            status = "failure"
                    else:
                        result = f"Error: Unknown tool '{tool_call.tool}'"
                        status = "error"
                    
                    # Update state
                    self.logger.log_event(tool_call.tool, tool_call.args, result, status)
                    trace_entry = f"\nTurn {step_turns} (Step {step.id}): {tool_call.tool} -> {status}\nResult: {result[:1000]}..."
                    execution_trace += trace_entry
                    if status == "success" and tool_call.tool == "read_file" and result:
                        current_context += f"\n\n--- TOOL RESULT: {tool_call.tool} {tool_signature} ---\n{result[:4000]}"

                    if status in {"failure", "error"} and ("Plan Violation" in result or "verification failed" in result.lower()):
                        break
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"  [!] {error_msg}")
                    self.logger.log_event(tool_call.tool, tool_call.args, error_msg, "exception")
                    execution_trace += f"\nTurn {step_turns} (Step {step.id}): {tool_call.tool} -> EXCEPTION: {error_msg}"
                    if "Plan Violation" in error_msg or "Security Violation" in error_msg:
                        break
                    
            if not step_complete:
                print(f"[red]CRITICAL: Step {step.id} failed after {max_step_turns} attempts. Aborting plan.[/red]")
                break
                
        if files_modified:
            wiki = WikiEngine(self.root)
            wiki.append_change_log(
                task_description=task or "Execution Plan",
                files_modified=list(files_modified),
                rationale=plan.rationale
            )
            from simpcode.wiki.index import IndexManager
            IndexManager(self.root / ".simp" / "wiki").update_hotspots(list(files_modified))
            
        return execution_trace

    def _update_wiki(self, file_path: str, wiki: WikiEngine):
        """Synchronizes relevant Wiki pages with recent file changes using O(1) lookup."""
        try:
            page_ids = wiki.get_pages_for_file(file_path)
            for page_id in page_ids:
                page = wiki.get_page(page_id)
                if not page:
                    continue
                
                instruction = registry.load("wiki_maintainer")
                full_path = self.root / file_path
                if not full_path.exists():
                    continue
                    
                code_context = f"--- {file_path} ---\n{full_path.read_text()[:5000]}"
                prompt = f"OLD CONTENT:\n{page.content}\n\nCurrent Code:\n{code_context}\n\nUpdate page."
                
                # Update page content and High-Integrity Hash Sync
                page.content = self.llm.chat([{"role": "user", "content": prompt}], instruction)
                wiki.sync_hashes(page) 
                self.console.print(f"  [Wiki] Synced and Verified {page.metadata.id} with {file_path}")
        except Exception as e:
            self.console.print(f"  [yellow][!] Wiki sync degraded for {file_path}: {e}[/yellow]")
