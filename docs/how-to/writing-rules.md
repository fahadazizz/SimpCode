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

- "Add request payload validation in `src/api/handlers.py`, add tests in `tests/test_handlers.py`, do not change auth middleware, verify with `pytest tests/test_handlers.py -q`."
- "Refactor `src/cache/service.py` to isolate eviction policy, update `tests/test_cache_service.py`, keep public API unchanged, verify with `pytest tests/test_cache_service.py -q`."

## 4. Examples of Weak Task Requests

- "Improve backend quality."
- "Make this project cleaner."
- "Fix auth completely."

Weak prompts lack file scope and verification expectations.

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
