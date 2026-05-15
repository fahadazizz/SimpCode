# File Ownership and Artifact Model

This page explains which files SimpCode owns, updates, or reads.

## 1. User-Owned vs SimpCode-Managed Files

### User-owned source files

Your application source files are still your files.

SimpCode may modify them only through approved plan execution scope.

### SimpCode-managed operational artifacts

SimpCode manages operational state under `.simp/` and selected top-level manifests.

## 2. Top-Level Project Artifacts

### `SIMP.md`

Primary project manifest used as high-priority context.

Can be updated through:

```text
/simp update <instruction>
```

### `SPEC.md`

Optional target-state/project spec.

Loaded into mandatory context when present.

## 3. `.simp/` Artifact Ownership

### `.simp/wiki/`

Wiki pages, index, changes log, and registry.

### `.simp/sessions/`

Serialized session states.

### `.simp/plans/`

Persisted plan artifacts.

### `.simp/logs/`

Execution traces.

### `.simp/tokens.log`

Token usage estimates.

### `.simp/registry.json`

Hash registry used by `HashRegistry` component.

## 4. Configuration Ownership

Config and history writable paths use global-first strategy:

1. `~/.simpcode/`
2. project-local `.simp/`

This means not all runtime files are guaranteed to live only under `.simp/`.

## 5. Git Considerations

On onboarding skeleton path, SimpCode appends `.simp/` to `.gitignore` only if `.gitignore` already exists.

If no `.gitignore` exists, you should add ignore rules manually based on your repository policy.

## 6. Write Boundaries During Execution

Writes are constrained by plan-approved targets.

If execution attempts to write outside scope, it is blocked as plan violation.

## 7. Suggested Team Policy

- Keep `SIMP.md` and `SPEC.md` versioned.
- Decide whether to version `.simp/wiki` based on workflow preference.
- Avoid versioning volatile session/log artifacts unless required for audit.
- Document your policy in repository contribution guidelines.
