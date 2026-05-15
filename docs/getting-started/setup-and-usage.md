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

Installation options and notes

- Quick installer (one-liner):

```bash
curl -fsSL https://raw.githubusercontent.com/fahadazizz/simpcode/main/install.sh | bash
```

	- This will clone the repository to `~/.local/share/simpcode`, create a virtual environment, install the package in editable mode, and create a symlink to the `simp` CLI in `~/.local/bin`.
	- To install from a fork or alternate repo, append the repository URL when invoking the script:

```bash
curl -fsSL https://raw.githubusercontent.com/fahadazizz/simpcode/main/install.sh | bash -s -- https://github.com/your-fork/simpcode.git
```

- Manual install (recommended for reproducible environments):

```bash
git clone https://github.com/fahadazizz/simpcode.git
cd simpcode
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

- Developer / contributor install (with dev extras):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Common post-install checks

- Ensure `${HOME}/.local/bin` is in your PATH if you used the installer script:

```bash
export PATH="$PATH:${HOME}/.local/bin"
```

- If you installed manually, ensure the virtualenv is activated before running `simp`.

Security note

- Inspect `install.sh` before running it. The one-liner downloads and executes a script — if you need to review it first, `curl -fsSL ... -o install.sh` and then open the file.

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
