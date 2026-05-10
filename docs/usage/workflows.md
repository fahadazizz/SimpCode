# Workflows

SimpCode supports two primary workflows: Knowledge Retrieval and Task Execution.

## Knowledge Retrieval (`ask`)

This workflow is used for understanding the codebase without making changes.

1.  **Mission:** User asks a question.
2.  **Scan:** SimpCode identifies relevant Wiki pages and project files.
3.  **Synthesis:** The LLM uses the gathered context to provide a grounded answer.
4.  **Usage:** `simp ask "Where are the API routes defined?"`

## Task Execution (`do`)

This workflow is used for implementing features, fixing bugs, or refactoring code.

1.  **Mission:** User describes a task.
2.  **Scan:** SimpCode researches the affected areas.
3.  **Plan:** SimpCode proposes a step-by-step plan, identifying risks and target files.
4.  **Review:** User inspects the plan and grants permission.
5.  **Execute:** SimpCode carries out the steps using the `ToolHarness`.
6.  **Verify:** SimpCode runs tests and updates the Wiki.
7.  **Usage:** `simp do "Implement a custom exception handler in the core module"`

## Wiki Maintenance (`sync`)

Keeping the semantic layer in sync with the code is critical for long-term accuracy.

1.  **Detect Drift:** `simp status` identifies if code changes have invalidated Wiki references.
2.  **Fix Hashes:** `simp sync` updates the stored hashes to match the current state of the code.
