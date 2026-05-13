# SimpCode

SimpCode is a **TUI-first engineering assistant** for real repositories. It is designed to help you understand a codebase, plan work safely, execute changes with verification, and keep a local project memory in sync as the repository evolves.

The current product model is intentionally simple:

- Use `simp setup` once to configure your provider.
- Use `simp init` to onboard a project and enter the interactive session.
- Do the actual engineering work inside the TUI with slash commands such as `/ask`, `/do`, `/sync`, `/status`, `/wiki`, and `/sessions`.

SimpCode is built around the current state of your repository, not a remote shared workspace. It keeps project artifacts local, uses a project manifest and optional specification file for alignment, and stores session history and wiki state inside `.simp/`.

## What SimpCode Gives You

- A local project memory that stays close to the code you are editing.
- A planning-first workflow that asks for structure before writing code.
- A terminal interface that is meant for real work, not just chat.
- Session persistence so you can return to a project later and continue from context.
- A safe execution model that keeps changes scoped and reviewable.

## Fast Start

```bash
cd /path/to/your/repository
python -m venv .venv
source .venv/bin/activate
pip install -e .

simp setup
simp init
```

After `simp init`, SimpCode opens the interactive shell. Inside the TUI, start with:

```text
/help
/ask what does this repository currently do?
/do add input validation to the API layer
```

## Where to Read First

- [User Guide](docs/guide.md): the full end-to-end walkthrough.
- [Documentation Portal](docs/index.md): navigation by task.
- [Getting Started](docs/getting-started/overview.md): install, configure, and launch.
- [Concepts](docs/concepts/index.md): the current mental model.
- [Reference](docs/reference/index.md): commands, files, and settings.
- [Troubleshooting](docs/TROUBLESHOOTING.md): common issues and recovery steps.

## Command Model

The CLI is intentionally small. The work commands live in the TUI.

| Command | Purpose |
|---|---|
| `simp setup` | Configure the global provider and model. |
| `simp init` | Onboard a repository and enter the TUI. |
| `simp chat` | Open the interactive session. |
| `simp help` | Show the CLI help and entry points. |

Inside the TUI, use slash commands for work:

| Slash command | Purpose |
|---|---|
| `/ask` | Research and explanation. |
| `/do` | Plan and execute a task. |
| `/sync` | Refresh the wiki after manual changes. |
| `/status` | Show current project health. |
| `/wiki` | Browse the knowledge base. |
| `/sessions` | Inspect saved sessions. |
| `/config` | View or change the active provider for the session. |

## Current Architecture in One Paragraph

`simp init` and `simp chat` open the TUI, which uses shared workflow functions for research, planning, execution, sync, status, recovery, wiki browsing, and session handling. The workflow layer reads project context, consults the wiki, assembles target source snippets, and coordinates the plan-and-execute loop. Session state is stored under `.simp/sessions/`, plan artifacts under `.simp/plans/`, and wiki content under `.simp/wiki/`.

## Repository Artifacts

These are the main files SimpCode cares about in a project repository:

- `SIMP.md`: the project manifest and current working overview.
- `SPEC.md`: the optional target-state specification.
- `.simp/wiki/`: the local knowledge base.
- `.simp/sessions/`: saved interactive sessions.
- `.simp/plans/`: persisted plans from task runs.

## Keep Reading

If you want the most complete walkthrough, open the [User Guide](docs/guide.md). If you want the task-by-task flows, go to [How To](docs/how-to/index.md). If you want the command syntax, open [Reference](docs/reference/index.md).
