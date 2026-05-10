# Core Logic

The `core` package contains the high-level reasoning and coordination logic for SimpCode.

## `ProjectAnalyzer`
**Location:** `src/simpcode/core/analyzer.py`
Used during `simp init` to bootstrap a project.
- **Stack Detection:** Identifies languages (Python, Node.js) and configuration files.
- **Command Inference:** Guesses the correct `pytest`, `flake8`, or `npm` commands for the project.

## `PlanGenerator`
**Location:** `src/simpcode/core/planner.py`
Converts a task and its context into a structured execution plan.
- **Schema:** Produces a `Plan` object containing `PlanStep`s.
- **Logic:** Considers invariants and risks to ensure the plan is safe and idiomatic.

## `TakeAction`
**Location:** `src/simpcode/core/executor.py`
Coordinates the execution of an approved plan.
- **Harness Integration:** Passes the plan's target files to the `ToolHarness`.
- **Iterative Reasoning:** Uses a "Mini-Step" logic to decide which specific tool to call for each plan step.

## `ScanScene`
**Location:** `src/simpcode/core/modes.py`
Implements the research phase of the agentic loop.
- **Context Assembly:** Combines mandatory files, Wiki pages, and project structure into a unified prompt context.
- **Budgeting:** Uses the `ContextBudgeter` to ensure the context fits within LLM token limits.
