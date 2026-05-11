# Deep Dive: Writing High-Quality Rules in AGENT.md

`AGENT.md` is the most powerful tool for ensuring SimpCode writes code that "looks like yours." While the Semantic Wiki provides context, `AGENT.md` provides **intent**.

---

## Structure of an Effective AGENT.md

A good `AGENT.md` acts as a condensed Style Guide. It should be written as a series of **immutable constraints**.

### 1. General Principles
Define the high-level philosophy of the codebase.
> "We prefer functional programming patterns over deep class hierarchies. Avoid shared mutable state at all costs."

### 2. Implementation Rules
Specific technical requirements that the AI must follow.
> - "Always use `pydantic` for data validation in API endpoints."
> - "Functions must not exceed 40 lines of code; refactor into sub-utilities if necessary."
> - "Use `snake_case` for variables and `PascalCase` for classes."

### 3. Documentation Requirements
Define how the AI should explain its work.
> - "All public methods require a Google-style docstring."
> - "Include complexity analysis (Time/Space) for all algorithms in `src/core/`."

---

## Common Mistakes to Avoid

### Being Too Vague
*   *Bad*: "Make the code clean."
*   *Good*: "Avoid nested if-statements. Use early returns and guard clauses."

### Including Temporary Tasks
`AGENT.md` is for **permanent rules**. For one-off tasks, use the `simp do` command argument.
*   *Bad*: "Next update: rename all files to lowercase." (Put this in a `simp do` command instead).

### Conflicting with the Tech Stack
Ensure your rules don't ask for a pattern that the current libraries don't support.

---

## Example AGENT.md for a Fast-API Project

```markdown
# Agent Instructions: SimpProject

## Philosophy
- Speed and safety are equal priorities.
- Use Asynchronous code (`async/await`) for all I/O operations.

## Patterns
- Dependency Injection must be used for database sessions.
- Use `JSONResponse` for all non-scalar API returns.
- Schema definitions belong in `src/schemas/`, not in `src/models/`.

## Testing
- No code is complete without a passing pytest in `tests/`.
- Mock all external API calls using `httpx-mock`.
```

---

## How SimpCode Uses This
For every turn of every mission, SimpCode reads `AGENT.md`. It is processed by the **Policy Engine** before the AI generates any code. If a generated snippet violates a rule in `AGENT.md`, the AI's internal reasoning loop identifies the conflict and regenerates the response.
