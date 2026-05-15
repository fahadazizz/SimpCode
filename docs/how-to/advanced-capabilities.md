# Advanced Capabilities

This guide covers advanced behaviors and how to use them intentionally.

## 1. Multi-Turn Planning with Additional Context Requests

Planner can request extra wiki pages instead of forcing a weak plan.

How to leverage this:

- provide clear task intent,
- allow dry-run plan generation,
- rerun after improving wiki/manifests if planner still lacks context.

## 2. Skill Injection for Task-Specific Reasoning

SimpCode can load skills from:

- global `~/.simpcode/skills/*.md`
- project `.simp/skills/*.md`

Project skills override global skills by matching skill ID.

Use this to encode repeatable domain reasoning patterns.

## 3. Execution Trace Auditing

Each execution writes JSONL traces in `.simp/logs/`.

Use trace logs to:

- inspect failed tool calls,
- detect repeated loop patterns,
- compare behavior across models/providers.

## 4. Controlled Recovery from Broken Runs

`/recover` loads latest plan artifact and asks approval.

Advanced practice:

- inspect latest plan JSON before recovery,
- compare with current repository state,
- if drift is high, rerun `/do` with narrower scope instead of force recovering.

## 5. Wiki Consistency as an Engineering Signal

Treat stale pages as signal:

- stale pages imply knowledge drift from source,
- run `/sync` before planning sensitive changes,
- use `changes` page and hotspots to audit recent mutation footprint.

## 6. Provider Strategy by Workflow Type

Practical strategy:

- high-fidelity planning tasks: prefer strongest structured-output model available,
- rapid exploratory tasks: use faster model,
- local-only environments: configure Ollama for privacy/control.

## 7. Operating With Strict Scope Discipline

For high-risk repositories:

- always use `/do --dry-run`,
- reject plans with broad or unclear targets,
- require explicit verification commands,
- split large tasks into multiple narrow `/do` runs.

## 8. Advanced Prompt Pattern

When issuing `/do`, include:

- files to touch,
- files not to touch,
- required verification command,
- expected acceptance criteria.

Example:

"Update `src/payments/retry.py` only, do not modify API handlers, add tests to `tests/test_retry.py`, verify with `pytest tests/test_retry.py -q`, and preserve existing public function signatures."
