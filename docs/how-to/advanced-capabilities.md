# Advanced Capabilities

This guide covers advanced behaviors and how to use them intentionally.

## 1. Multi-Turn Planning with Additional Context Requests

Planner can request extra wiki pages instead of forcing a weak plan.

How to leverage this:

- provide clear task intent,
- allow dry-run plan generation,
- rerun after improving wiki/manifests if planner still lacks context.
- global `~/.simpcode/skills/*.md`
- project `.simp/skills/*.md`
## 3. Execution Trace Auditing

- detect repeated loop patterns,
- compare behavior across models/providers.
Advanced practice:

## 5. Wiki Consistency as an Engineering Signal

- use `changes` page and hotspots to audit recent mutation footprint.

- rapid exploratory tasks: use faster model,
- local-only environments: configure Ollama for privacy/control.
- always use `/do --dry-run`,
- reject plans with broad or unclear targets,
- require explicit verification commands,
# Advanced Capabilities

This page explains operational features you will use when you need more control: index generation, token budgeting, provider switching, and wiki maintenance.

Index generation and token budgeting
----------------------------------

`IndexManager` constructs `index.md` by selecting the most relevant wiki pages under a token budget. If the assembled index exceeds the token budget, SimpCode prunes lower-priority sections (hotspots, decisions, modules) to fit the budget.

When to use:

- large repositories where a full context exceeds the model token limit,
- reducing the context the planner receives to improve response stability.

Provider switching and model experimentation
-------------------------------------------

You can switch providers and models during a session with `/config` or `simp setup`.

Examples:

```text
/config --provider openai
/config --model gpt-4o-mini
```

Recommendations:

- For deterministic plan structure testing, use smaller models or fixed temperature settings.
- For synthesis-heavy tasks (onboarding, bootstrap), prefer larger-capacity models.

Wiki maintenance and staleness handling
--------------------------------------

Use `/status` to list stale pages. `/sync` will attempt to regenerate stale pages using the current project context. The Wiki Engine maintains a file->page registry for fast lookups and uses cached mtime checks to avoid expensive rescans.

When to run manual maintenance:

- after large refactors that move or delete many files,
- when onboarding a repo that had no previous `.simp/wiki` artifacts.

Advanced recipes
----------------

1) Rebuild index with a smaller token budget

```text
# edit .simp/config or use interactive config to reduce token budget
/do rebuild index --dry-run
```

2) Test a plan under a different provider

```text
/config --provider openai
# regenerate the plan or re-run the previous dry-run
/do <task> --dry-run
```
- split large tasks into multiple narrow `/do` runs.

## 8. Advanced Prompt Pattern

When issuing `/do`, include:

- files to touch,
- files not to touch,
- required verification command,
- expected acceptance criteria.

Example:

"Update `src/payments/retry.py` only, do not modify API handlers, add tests to `tests/test_retry.py`, verify with `pytest tests/test_retry.py -q`, and preserve existing public function signatures."
