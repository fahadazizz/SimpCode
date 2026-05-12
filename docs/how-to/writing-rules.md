# Deep Dive: Writing a Strong SPEC.md

`SPEC.md` is the most powerful tool for ensuring SimpCode builds toward the project you actually want. While the Semantic Wiki provides context, `SPEC.md` provides **intent**.

---

## Structure of an Effective SPEC.md

A good `SPEC.md` acts as a compact product and architecture contract. It should be written as a series of **clear requirements**.

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
`SPEC.md` is for **project-defining requirements**. For one-off tasks, put the requirement directly in the `simp do` command or update the relevant section of `SPEC.md` first.
*   *Bad*: "Next update: rename all files to lowercase." (Put this in a `simp do` command instead).

### Conflicting with the Tech Stack
Ensure your rules don't ask for a pattern that the current libraries don't support.

---

## Example SPEC.md for a FastAPI Project

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
For every turn of every mission, SimpCode reads `SPEC.md` and the semantic Wiki. The internal prompt layer then uses those requirements before the AI generates any code. If a generated snippet conflicts with the specification, the reasoning loop identifies the mismatch and regenerates the response.
