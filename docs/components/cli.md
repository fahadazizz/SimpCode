# CLI Interface

The CLI is the primary entry point for users. It is built using the `click` library and follows a standard command-based interface.

**Location:** `src/simpcode/cli/main.py`

## Commands

### `init`
Onboards SimpCode to a project.
- **Action:** Runs `ProjectAnalyzer` to detect the tech stack and generates initial `SIMP.md` and `AGENT.md` files.
- **Usage:** `simp init`

### `ask <question>`
Performs a read-only query against the codebase.
- **Action:** Runs the `ScanScene` mode to gather context and provides an LLM-generated answer.
- **Usage:** `simp ask "How is authentication implemented?"`

### `do <task>`
Executes a codebase-modifying task.
- **Action:** Runs `ScanScene`, then `PlanGenerator`, presents the plan for approval, and finally runs `TakeAction`.
- **Options:** 
  - `--yes`: Skip the approval gate.
  - `--dry-run`: Show the plan but do not execute.
- **Usage:** `simp do "Add a new endpoint to the users module"`

### `sync`
Verifies and refreshes the Wiki state.
- **Action:** Checks file hashes for all source references in the Wiki. If drift is detected, it updates the hashes.
- **Usage:** `simp sync`

### `status`
Displays the health of the SimpCode setup.
- **Action:** Shows how many Wiki pages are tracked and lists any that are currently stale.
- **Usage:** `simp status`

### `wiki`
(Stub) Interface for managing and inspecting Wiki pages directly.

### `recover`
(Stub) Resumes or reverts an interrupted session.
