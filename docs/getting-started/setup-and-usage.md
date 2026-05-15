# Setup and Usage

This document walks through setup plus real usage patterns in sequence.

## 1. Initial Setup Sequence

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
simp setup
simp init
```

Inside TUI:

```text
/help
/config
/status
```

## 2. Understand the Two Interfaces

### CLI commands

Useful for setup and direct single-action calls:

- `simp setup`
- `simp init`
- `simp ask ...`
- `simp do ...`
- `simp sync`
- `simp status`
- `simp recover`

### Interactive TUI commands

Use slash commands for iterative workflows and persistent context.

## 3. First Productive Session

Suggested flow:

```text
/ask summarize the architecture and top risk areas in this repository
/wiki list
/wiki show index
/do add input validation in src/... and tests in tests/... --dry-run
/do add input validation in src/... and tests in tests/...
```

## 4. When To Use `/ask` vs `/do`

Use `/ask` when you need:

- understanding,
- design tradeoff discussion,
- non-mutating exploration.

Use `/do` when you need:

- structured implementation plan,
- explicit approval gate,
- bounded execution with verification.

## 5. Managing Configuration Mid-Session

Check active settings:

```text
/config
```

Change provider/model:

```text
/config --provider <provider>
/config --model <model-id>
```

These values persist with session state.

## 6. Session Usage Pattern

List sessions:

```text
/sessions
```

Switch session:

```text
/sessions --switch <session-id>
```

When starting TUI without explicit session, SimpCode loads latest session when available.

## 7. Keeping Wiki Healthy

Before major work:

```text
/status
```

If stale pages exist:

```text
/sync
```

Then continue task execution.

## 8. Recovery and Continuity

If execution was interrupted:

```text
/recover
```

This loads latest saved plan artifact and asks approval before continuing.

## 9. Practical Operating Rules

- always review dry-run plans for medium/high-risk changes,
- include explicit target files in tasks,
- include concrete verification command expectations,
- run `/status` after significant edits,
- inspect `.simp` artifacts when behavior seems inconsistent.
