# SimpCode User Guide

This guide is the practical, end-to-end path for using SimpCode as your daily engineering assistant.

It is written for users who want to:

- onboard a repository correctly,
- understand what SimpCode is doing behind the scenes,
- execute tasks safely,
- recover from failures,
- and keep project knowledge synchronized with source changes.

## 1. Mental Model

SimpCode is a local engineering loop with strong structure:

1. Understand context (`ScanScene`)
2. Produce a plan (`PlanGenerator`)
3. Ask for explicit approval (`PermissionSystem`)
4. Execute with scoped tools (`ToolHarness`)
5. Verify and log outcomes (`ExecutionLogger` + step verification)
6. Sync and evolve knowledge (`WikiEngine` + change log + hotspots)

In practice, you mostly interact through the TUI using slash commands.

## 2. Installation and First Run

From your repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Configure your provider once:

```bash
simp setup
```

Then initialize and enter the TUI:

```bash
simp init
```

You can also start the TUI directly with:

```bash
simp
```

Notes:

- The installed command entrypoint is `simp`.
- `simp` with no subcommand launches the interactive shell.
- `simp init`, `simp ask`, and `simp do` all trigger onboarding checks automatically.

## 3. What Onboarding Creates

Onboarding is considered required when either of these is missing:

- `SIMP.md`
- `.simp/wiki/index.md`

When required, SimpCode creates baseline artifacts:

- `SIMP.md`
- `SPEC.md`
- `.simp/wiki/index.md`
- `.simp/wiki/patterns.md`
- `.simp/wiki/risks.md`
- `.simp/wiki/invariants.md`
- `.simp/wiki/seams.md`
- `.simp/wiki/flows.md`
- `.simp/wiki/changes.md`
- directory scaffolding under `.simp/wiki/modules`, `.simp/wiki/symbols`, `.simp/wiki/decisions`

Behavior details:

- If the project looks like a skeleton, static templates are used.
- If codebase metadata is rich enough, SimpCode attempts synthesized onboarding and wiki bootstrap.
- If synthesis fails, SimpCode falls back to skeleton initialization.

## 4. TUI Daily Workflow

Inside the TUI, you can either type plain text (chat turn) or slash commands.

### Essential slash commands

- `/ask <question>`: research and explanation, no direct execution plan.
- `/do <task> [--yes] [--dry-run]`: create plan, optionally auto-approve or dry-run.
- `/status`: current project and wiki freshness summary.
- `/sync`: regenerate stale wiki pages based on source references.
- `/wiki list`: list wiki pages and freshness.
- `/wiki show <page-id>`: show one wiki page.
- `/recover`: load most recent saved plan and resume execution after approval.
- `/sessions`: list sessions.
- `/sessions --switch <session-id>`: load a previous session.
- `/config`: show current provider/model/session/project.
- `/config --provider <name>`: set provider for current session.
- `/config --model <model-id>`: set model for current session.
- `/simp show`: display current `SIMP.md`.
- `/simp update <instruction>`: propose and optionally apply `SIMP.md` update.
- `/clear`: clear in-memory conversation history for current session state.
- `/help`: command help.
- `/exit`: save and quit.

### Plain text chat turns

If you type text without a leading slash, SimpCode:

1. runs contextual scan,
2. sends context + conversation history to the interactive assistant prompt,
3. streams the response if provider supports streaming,
4. saves both user and assistant messages to session history.

## 5. The `/do` Lifecycle in Detail

When you run `/do`:

1. Context scan is assembled.
2. Planner creates a structured `Plan` with steps, rationale, risk level, and verification criteria.
3. Plan is persisted under `.simp/plans/plan_<task_id>.json`.
4. You approve unless `--yes` is used.
5. Executor runs each step in a bounded multi-turn loop.
6. File changes are constrained to plan-approved targets.
7. Inline verification runs:
   - structural lint command `flake8 <file>` after write/patch,
   - then step verification command if provided.
8. Execution trace is logged to `.simp/logs/exec_<session_id>.jsonl`.
9. If files changed, wiki change log and hotspots are updated.
10. Session status is updated (`planned`, `running`, `completed`, `aborted`, `interrupted`).

### Failure handling during `/do`

- Per step, repeated failures are bounded.
- Repeated identical tool loops are detected and aborted.
- Plan or security violations stop affected actions.
- Keyboard interrupt saves interrupted session state.

## 6. Safety and Scope Model

SimpCode enforces two distinct scopes:

- Read scope: project-wide, with exclusion patterns.
- Write scope: restricted to files approved by the plan.

Security gates include:

- path normalization and traversal blocking,
- excluded pattern filtering (`.env`, keys, `.git`, `.simp`, etc.),
- shell command allowlist with shell operator rejection,
- explicit plan-violation checks before writes.

## 7. Wiki Freshness and Synchronization

Wiki pages store source references with hashes.

Freshness logic:

- `check_staleness` compares current hash to stored hash per source.
- stale pages can be regenerated from code.

Performance behavior:

- file-to-page lookup uses registry dictionary (`get_pages_for_file`) for O(1) retrieval,
- page save updates registry via source-based cleanup (O(s) for tracked sources),
- page discovery uses directory mtime cache for fast repeated status calls.

## 8. Sessions and Persistence

Sessions live in `.simp/sessions/<session_id>.json` and include:

- chat history,
- selected provider/model,
- task history,
- produced plans,
- errors,
- status and timestamps.

Automatic behavior:

- TUI starts with latest session if present,
- you can switch manually with `/sessions --switch`.

## 9. Provider and Configuration

Global/default provider config is managed via `simp setup`.

Supported provider names in setup:

- `groq`
- `anthropic`
- `openai`
- `openrouter`
- `google`
- `ollama`

Configuration storage resolves writable location in this priority:

1. `~/.simpcode/config.json`
2. fallback to `<project>/.simp/config.json`

Session-level overrides through `/config` affect current session state.

## 10. Practical Best Practices

- Keep `SIMP.md` and `SPEC.md` meaningful. They are always high-priority context.
- Prefer `/do --dry-run` before risky, broad changes.
- Keep verification commands concrete in your task framing.
- Use `/status` before and after major edits.
- Run `/sync` after substantial manual code changes outside SimpCode.
- Use `/recover` when execution was interrupted and you want continuity.

## 11. Known Command Nuances

Current behavior nuances you should know:

- `/wiki search` exists but currently prints “coming soon”.
- `/clear` clears history; there is no implemented `--full` mode logic.
- `simp chat` is not a separate CLI subcommand in current code.

Use `simp` (no subcommand) or `simp init` for TUI entry.

## 12. Next Reading

- [How-To Guides](how-to/index.md)
- [Reference](reference/index.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)
