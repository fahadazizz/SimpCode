# Operational Modes

SimpCode operates through five distinct modes. This structured approach ensures that the assistant always acts with full context and within safety boundaries.

## 1. GET MISSION
In this initial mode, SimpCode captures the user's intent. This happens through commands like `simp ask` or `simp do`. The "mission" is the high-level goal that the assistant must achieve.

## 2. SCAN SCENE
This is the research phase. 
- **Wiki Navigation:** The `WikiNavigator` consults the `index.md` to identify relevant semantic pages.
- **Context Assembly:** The `ContextBudgeter` gathers mandatory files (`SIMP.md`, `AGENT.md`), relevant Wiki pages, and code snippets into a single context string.
- **Mode Implementation:** Found in `src/simpcode/core/modes.py` as `ScanScene`.

## 3. THINK THROUGH
Before modifying any code, SimpCode must reason about the implementation.
- **Plan Generation:** The `PlanGenerator` uses the LLM to create a `Plan` object.
- **Risk Assessment:** Every plan includes a risk level (Low, Medium, High) and scope exclusions.
- **Invariants & Risks:** The planner explicitly considers architectural invariants and potential side effects.

## 4. TAKE ACTION
The execution phase where the plan is carried out.
- **Approval Gate:** The user must approve the plan before execution (unless `--yes` is used).
- **Restricted Harness:** Commands and file writes are filtered through the `ToolHarness`. Only files listed in the plan are writable.
- **Read-Before-Write:** The executor ensures it understands the current state of a file before applying changes.

## 5. GET BETTER
The final phase focuses on maintaining system integrity.
- **Verification:** Runs tests and linters to confirm the change works and hasn't introduced regressions.
- **Wiki Update:** If the code changes, the `ToolHarness` automatically updates the associated hashes in the Wiki to prevent staleness.
- **Sync:** The `simp sync` command can be used to perform batch freshness checks.
