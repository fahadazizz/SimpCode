# SimpCode Troubleshooting

This guide is organized by symptoms you are likely to encounter in daily usage.

## 1. SimpCode Does Not Start

### Symptom

Running `simp` fails immediately.

### Checklist

1. Ensure your virtual environment is active.
2. Ensure package is installed in editable mode:

```bash
pip install -e .
```

3. Verify Python version is compatible (`>=3.12`).
4. Run:

```bash
simp --help
```

If this still fails, reinstall dependencies:

```bash
pip install -e . --upgrade
```

## 2. Provider Errors or Empty LLM Responses

### Symptom

- Provider auth errors
- rate limit errors
- missing API key behavior

### Root causes

- provider not configured in `simp setup`
- API key not present or invalid
- model ID unsupported by selected provider

### Fix

1. Re-run setup:

```bash
simp setup
```

2. Confirm provider/model in session:

```text
/config
```

3. Override provider/model if needed:

```text
/config --provider <name>
/config --model <model-id>
```

4. For Ollama, verify base URL and local server availability.

## 3. Onboarding Not Triggering or Incomplete

### Symptom

`/ask` or `/do` runs with poor context, or expected files are missing.

### Expected onboarding trigger

Onboarding runs when either is missing:

- `SIMP.md`
- `.simp/wiki/index.md`

### Fix

From project root:

```text
/init
```

Then verify these paths exist.

If onboarding synthesis failed previously, skeleton fallback still creates core files.

## 4. `/do` Aborts Early

### Symptom

Task starts then exits with plan violation, security violation, or repeated tool call loop detection.

### Typical causes

- Planner target too broad or wrong file target
- Attempted write outside allowed plan scope
- repeated identical tool calls indicate reasoning loop

### Fix

1. Run dry run first:

```text
/do <task> --dry-run
```

2. Verify step targets are concrete and correct.
3. Reword task with explicit files.
4. Re-run with approval and monitor first failing step.

## 5. Verification Fails After File Update

### Symptom

Execution reports lint or verification failure.

### What happens internally

After write/patch, executor runs:

- `flake8 <file>`
- then `step.verification` if provided

### Fix

- correct linting problems first,
- make verification commands deterministic and available,
- ensure dependencies for verification commands are installed.

## 6. Wiki Shows Stale Pages

### Symptom

`/status` reports stale pages.

### Fix

Run:

```text
/sync
```

Then inspect:

```text
/wiki list
/wiki show <page-id>
```

If source files were deleted, some pages may remain stale/excluded until references are updated.

## 7. Session Switching Confusion

### Symptom

You expected old context but see a different history.

### Fix

1. List sessions:

```text
/sessions
```

2. Switch explicitly:

```text
/sessions --switch <session-id>
```

3. Confirm active session via `/config`.

## 8. Recovery Did Not Resume Expected Work

### Symptom

`/recover` loads a plan but not the one you intended.

### Behavior

`/recover` uses the latest modified plan file in `.simp/plans/`.

### Fix

- inspect `.simp/plans/` timestamps,
- if needed, manually load and review plan JSON,
- rerun task with explicit scope if plan is outdated.

## 9. Shell Command Rejected in Executor

### Symptom

Security violation for a shell command.

### Cause

`run_shell` only permits an allowlist and rejects shell operators.

### Fix

- use simple direct commands,
- avoid pipes/redirection/chaining,
- rely on multiple verified steps instead of one complex shell line.

## 10. Configuration File Location Confusion

### Behavior

SimpCode tries to write config/history globally first:

- `~/.simpcode/`

If unavailable, it falls back to project-local:

- `.simp/`

### Fix

Check both locations when debugging config drift.

## 11. Known Current Limitations

- Some command handlers or CLI paths may be incomplete or have evolved; verify current behavior with `simp --help` or by inspecting the CLI sources in `src/simpcode/cli/`.

If you encounter mismatched documentation, please open an issue or update the relevant docs entry to reflect the current implementation.

## 12. Debugging Workflow for Persistent Problems

1. Verify install and Python environment.
2. Verify provider configuration and model.
3. Re-run onboarding (`/init`).
4. Run `/status` and `/sync`.
5. Run `/do ... --dry-run` and inspect plan quality.
6. Check `.simp/logs/exec_*.jsonl` for execution failures.
7. Check `.simp/sessions/*.json` for state drift.
8. Reproduce with smallest possible task scope.

This sequence isolates most real-world issues quickly.
