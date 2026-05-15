# Writing Rules and Prompting Guidance

This guide explains how to write prompts and task requests that produce reliable SimpCode behavior.

## 1. The Core Rule

Ambiguous scope creates weak plans.

Precise scope creates reliable plans.

## 2. Prompt Structure Template

Use this shape for `/do` requests:

1. objective
2. exact target files
3. explicit exclusions
4. verification command
5. constraints (style, compatibility, performance)

Example template:

"Implement <objective> in <target files>. Do not modify <excluded files>. Verify with <command>. Preserve <constraints>."

## 3. Examples of Strong Task Requests


# Writing Rules and Prompt Guidance

Good task descriptions make planning predictable and reviewable. When writing requests for `/do`, follow these rules:

1. Be specific about targets

- Prefer exact file paths and, when appropriate, line ranges.
- Example: `src/api/handlers.py` not `the API layer`.

2. Include verification

- Always suggest a verification step: a unit test, `flake8`, or a small integration test.
- Example: `verify with pytest tests/test_handlers.py -q`.

3. Limit scope

- Keep single `/do` tasks focused (1–3 files). For larger work, split into phases and use `--dry-run` for review.

4. State exclusions

- If there are files or areas that must not be changed, explicitly list them in the task.

Good vs Bad examples

Good:

```text
Add input validation to src/api/handlers.py, update tests in tests/test_handlers.py, verify with pytest tests/test_handlers.py -q
```

Bad:

```text
Fix all API bugs across the repo
```

Templates

Use this template for predictable plans:

```text
/do <short goal> in <file(s)>; tests: <test command>; exclude: <paths>
```

Example:

```text
/do add token expiry check in src/auth/tokens.py; tests: pytest tests/test_tokens.py -q; exclude: migrations/

## 5. Writing Effective `/ask` Questions

Good `/ask` questions:

- ask about architecture boundaries,
- ask about risk areas and invariants,
- ask for file-level orientation before `/do`.

Examples:

- "Where does request authorization currently happen, and what assumptions does it make?"
- "Which modules are coupled to persistence layer decisions?"

## 6. Recovery-Oriented Prompting

When recovering from failure, mention failure context explicitly:

- previous failing command,
- exact error symptom,
- desired non-breaking constraint.

This improves planning quality for corrective tasks.

## 7. Verification Guidance

Always provide a verification command that can run in your environment.

Preferred:

- targeted unit/integration tests,
- project lint/type checks for touched files.

Avoid vague verification instructions such as "make sure it works".

## 8. Scope Exclusion Guidance

Explicitly state exclusion boundaries in task text:

- "Do not modify migrations"
- "Do not change public API signatures"
- "Do not touch deployment config"

This helps planner emit safer scope exclusions.

## 9. Iteration Pattern for Difficult Tasks

For complex work, split into phases:

1. `/ask` architecture and dependency analysis
2. `/do ... --dry-run` for planned phase 1
3. `/do ...` phase 1 execution
4. validate and repeat for phase 2

This reduces risk compared to one broad task request.
