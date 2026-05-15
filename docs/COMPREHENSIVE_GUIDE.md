# SimpCode Comprehensive Guide

This guide is a long-form operational manual for users who want to use SimpCode deeply and safely.

It combines daily usage, strategic patterns, and implementation-informed behavior.

## 1. Who This Guide Is For

Use this guide if you are:

- an engineer integrating SimpCode into normal development cycles,
- a tech lead wanting reviewable and recoverable AI-assisted execution,
- a maintainer who needs confidence in what SimpCode can and cannot do today.

## 2. Product Positioning

SimpCode is a local engineering assistant optimized for:

- repository-aware context,
- planning before mutation,
- constrained execution with verification,
- artifact persistence and recovery.

SimpCode is not optimized for:

- free-form unrestricted shell automation,
- hidden cloud workspace abstraction,
- replacing human review on high-risk changes.

## 3. End-to-End Lifecycle

### Setup lifecycle

1. install package and dependencies,
2. configure provider with `simp setup`,
3. initialize repository with `simp init`.

### Task lifecycle

1. ask or do command enters workflow engine,
2. context is assembled from source + wiki + skills,
3. planner generates structured plan,
4. user approves plan,
5. executor runs with safety gates and verification,
6. wiki and logs updated.

### Recovery lifecycle

1. inspect sessions/plans,
2. run `/recover` to resume latest plan,
3. rerun with narrower scope if needed.

## 4. User Workflow Patterns

### Pattern A: research-first

- `/ask` architectural question
- inspect `/wiki list`
- run `/status`
- then run scoped `/do`

### Pattern B: safe execution-first

- `/do ... --dry-run`
- review plan targets and verification commands
- approve with `/do ...`

### Pattern C: interrupted session recovery

- restart TUI
- check `/sessions`
- switch session or `/recover`
- verify wiki freshness with `/status` and `/sync`

## 5. Effective Task Prompting

For reliable planning and execution, include:

- target files or directories,
- explicit constraints,
- concrete verification command expectations,
- known exclusions.

Good example:

"Update request validation in `src/api/handlers.py`, add tests in `tests/test_handlers.py`, and verify with `pytest tests/test_handlers.py -q`."

Less effective example:

"Improve backend quality."

## 6. Managing Scope and Risk

SimpCode exposes risk level in generated plans.

Use this signal operationally:

- low risk: likely safe for direct approval after review,
- medium risk: require dry-run review,
- high risk: tighten scope and split tasks before approval.

Always inspect:

- step targets,
- verification commands,
- scope exclusions.

## 7. Wiki Strategy for Long-Running Projects

Treat `.simp/wiki/` as your local semantic memory.

Operational recommendations:

- run `/sync` after significant manual edits,
- watch stale page counts with `/status`,
- inspect cognitive pages (`patterns`, `risks`, `invariants`, `flows`, `seams`) routinely,
- keep `SIMP.md` current so model instruction framing reflects project reality.

## 8. Session Hygiene

Use sessions intentionally:

- keep related work in one session where possible,
- switch sessions for unrelated streams,
- clear history (`/clear`) when prompt drift appears,
- inspect saved session JSON when debugging memory effects.

## 9. Observability and Auditability

When you need evidence of behavior:

- plans: `.simp/plans/*.json`
- execution traces: `.simp/logs/exec_*.jsonl`
- sessions: `.simp/sessions/*.json`
- token logs: `.simp/tokens.log`
- wiki changes: `.simp/wiki/changes.md`

These files make SimpCode easier to trust and debug than systems with opaque transient memory.

## 10. Working With Provider Differences

Different providers may vary in:

- structured output reliability,
- response speed,
- cost,
- context handling quality.

If planning quality degrades:

1. switch model with `/config --model`,
2. narrow task scope,
3. re-run dry-run planning.

## 11. Common Failure Modes and Controls

### Failure mode: broad ambiguous plans

Control: use explicit file targets and dry-run.

### Failure mode: verification command not available

Control: install missing tooling or change task to use available verification.

### Failure mode: stale wiki context after manual changes

Control: run `/sync` and re-check `/status`.

### Failure mode: shell command blocked by policy

Control: break command into policy-compatible steps.

## 12. Team Operating Model

For team adoption:

- define team conventions for `/do` task formatting,
- require dry-run for medium/high-risk changes,
- review plan artifacts in PRs for critical work,
- include `.simp/wiki/changes.md` review in release readiness checks.

## 13. Upgrade Readiness Checklist

Before upgrading SimpCode or prompts:

1. run core test suite,
2. validate `ask`, `do`, `sync`, `status`, `recover` paths,
3. verify provider configuration migration,
4. compare generated plan quality on representative tasks,
5. validate wiki freshness and cache behavior.

## 14. What To Read Next

- [How-To Guides](how-to/index.md)
- [Reference](reference/index.md)
- [Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)
