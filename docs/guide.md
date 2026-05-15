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
# User Guide — Practical Workflows

This User Guide shows concrete, repeatable workflows for getting value from SimpCode while minimizing risk. It is written for engineers and reviewers who will operate SimpCode day-to-day.

Flows covered here:

- Investigate: gather targeted context and confirm relevant files.
- Plan: produce a reviewable plan with explicit targets and verification.
- Execute: run approved steps with automatic verification and audit logs.
- Recover: resume interrupted work safely.

1) Investigate (non-mutating)
--------------------------------

Goal: Quickly learn where a concern lives without changing files.

Command:

```text
/ask "Where is request validation performed for the payments API?"
```

What to expect:

- A short answer summarizing likely files and design assumptions.
- Suggested wiki pages or files to inspect (e.g., `src/payments/service.py`, `SIMP.md`).
- Follow-ups such as `/ask` for deeper dives or `/wiki show <page-id>` to read a wiki page.

2) Create and review a plan (dry-run)
-------------------------------------

Goal: Ask SimpCode to prepare an actionable plan without making changes.

Command:

```text
/do add input validation to src/api/handlers.py and tests in tests/test_handlers.py --dry-run
```

What to inspect in the plan:

- Exact target files and line ranges.
- For each step: action, tool to use (`write_file`/`patch_file`), and the verification command.
- Scope exclusions (files the plan will not touch).
- Risk level and suggested reviewer.

Approve when satisfied (see Execute).

3) Execute an approved plan
----------------------------

Command:

```text
/do add input validation to src/api/handlers.py and tests in tests/test_handlers.py --yes
```

Execution behavior:

- The executor enforces a write scope derived from the plan.
- After each change, it runs lint and the step's verification command.
- All actions and outputs are appended to `.simp/logs/exec_<session>.jsonl` for auditing.

If a verification step fails, the executor stops the step and records the failure. You can then inspect the trace and re-run a corrected plan.

4) Recovering interrupted work
------------------------------

If your session or machine crashed, resume with:

```text
/recover
```

`/recover` loads the most recent persisted plan and asks for approval before continuing execution.

Best practices
--------------

- Always run `/status` and `/sync` before executing plans that modify many files.
- Use `--dry-run` for medium- and high-risk tasks and require a human reviewer for approval.
- Keep verification commands small and deterministic (unit tests, linters).
- Inspect `.simp/plans/` and `.simp/logs/` when troubleshooting unexpected behavior.

Example — full safe loop
------------------------

```text
/status
/ask "Summarize critical auth paths and outstanding risks"
/do add token expiry checks in src/auth/tokens.py and tests --dry-run
# Review plan, then:
/do add token expiry checks in src/auth/tokens.py and tests --yes
/sync
/status
```

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
