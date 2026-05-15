# SimpCode

SimpCode is a local, TUI-first engineering assistant for real repositories.

It is designed to help you:

- understand a codebase with structured context,
- generate safe implementation plans,
- execute approved changes with constrained tooling,
- keep a local wiki and session memory synchronized with source reality.

SimpCode is intentionally artifact-driven: most important runtime state is persisted under `.simp/` and can be inspected.

## Why SimpCode Exists

Many AI coding workflows fail because they blur boundaries:

- hidden context,
- implicit writes,
- weak recovery,
- poor observability.

SimpCode takes the opposite path:

- explicit planning before mutation,
- scoped write permissions,
- inline verification,
- persistent plans, sessions, logs, and wiki pages.

## Fast Start

From your repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

simp setup
simp init
```

Inside the TUI:

```text
/help
/status
/ask what does this repository currently do?
/do add input validation to the API layer --dry-run
```

## Command Model

### CLI entrypoint

- `simp` with no subcommand starts interactive TUI.

### CLI commands

- `simp setup`
- `simp init`
- `simp ask <query>`
- `simp do <task> [--yes] [--dry-run]`
- `simp sync`
- `simp status`
- `simp wiki <args>`
- `simp recover`

### TUI slash commands

- `/ask`
- `/do`
- `/sync`
- `/status`
- `/recover`
- `/init`
- `/wiki list`
- `/wiki show <page-id>`
- `/sessions`
- `/sessions --switch <session-id>`
- `/config`
- `/config --provider <name>`
- `/config --model <model-id>`
- `/simp show`
- `/simp update <instruction>`
- `/clear`
- `/help`
- `/exit`

## What SimpCode Creates in Your Repo

Onboarding creates or maintains:

- `SIMP.md`
- `SPEC.md`
- `.simp/wiki/` pages and structure
- `.simp/sessions/` saved sessions
- `.simp/plans/` persisted plans
- `.simp/logs/` execution traces
- `.simp/tokens.log` token usage estimates

### Wiki highlights

- source-hash freshness checks,
- stale page regeneration,
- file-to-page registry for efficient lookup,
- append-only style change log (`changes.md`),
- project index with hotspot updates.

## Safety and Reliability Model

SimpCode execution is constrained by design.

- reads are broad but filtered by exclusions,
- writes are restricted to plan-approved targets,
- shell usage is allowlisted and rejects dangerous shell operators,
- writes are followed by lint and optional verification command checks.

When execution fails or is interrupted, state remains recoverable via persisted artifacts.

## Provider Configuration

`simp setup` supports:

- `groq`
- `anthropic`
- `openai`
- `openrouter`
- `google`
- `ollama`

Config persistence prefers:

1. `~/.simpcode/config.json`
2. fallback `<project>/.simp/config.json`

## Documentation

Start here:

- [Documentation Portal](docs/index.md)
- [User Guide](docs/guide.md)
- [Reference](docs/reference/index.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Architecture Deep Dive](docs/ARCHITECTURE_DEEP_DIVE.md)

## Architecture Overview

A concise map of the major SimpCode components and where to find their implementation:

- **CLI / TUI**: `src/simpcode/cli/` — `SimpShell` routes user commands and manages session interaction.
- **Planner**: `src/simpcode/core/planner.py` — prepares structured plans using the LLM.
- **Executor**: `src/simpcode/core/executor.py` — executes approved steps via `ToolHarness`, performs verification, and updates the wiki.
- **Wiki Engine & Indexing**: `src/simpcode/wiki/` — maintains wiki pages, the file->page registry (`.simp/wiki/registry.json`), and `index.md` generation.
- **LLM Client**: `src/simpcode/core/llm/` — provider adapters and structured output helpers.
- **Tooling & Safety**: `src/simpcode/harness/tools.py` and `src/simpcode/harness/permissions.py` — path scoping, write approvals, and shell allowlist.

For a deeper, implementation-level description and diagrams, see the Architecture Deep Dive: [docs/ARCHITECTURE_DEEP_DIVE.md](docs/ARCHITECTURE_DEEP_DIVE.md)

If you are implementing workflow conventions for teams, also read:

- [Comprehensive Guide](docs/COMPREHENSIVE_GUIDE.md)

## Current Known Nuances

Current implementation details worth noting:

- `/wiki search` command path is placeholder text in current TUI handler.
- `/clear --full` is described in command registry text, but implemented behavior is `/clear` only.
- There is no dedicated `simp chat` subcommand; use `simp` or `simp init` for interactive mode.

## Development and Validation

Run tests:

```bash
PYTHONPATH=src python -m pytest tests/ -q
```

SimpCode has dedicated performance and regression tests for wiki behavior, including scale and cache checks.

## License and Usage Context

SimpCode is optimized for local engineering assistance with explicit user oversight. Treat generated plans and modifications as reviewable outputs, not unreviewed production truth.
