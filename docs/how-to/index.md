# How-To Guides

This section provides concise recipes for common tasks. Each recipe lists a goal, the commands to run, and verification steps.

Guides

- [Advanced Capabilities](advanced-capabilities.md)
- [Writing Rules and Prompting Guidance](writing-rules.md)

Common recipes

Run a safe implementation cycle

Goal: Make a small, reviewable change with tests and verification.

Commands:

1. `/status`
2. `/do <task> --dry-run`  # review the generated plan
3. approve the plan if targets and verifications look correct
4. `/do <task> --yes`
5. `/sync`
6. `/status`

Resume interrupted work

Goal: Recover the latest plan and resume safely.

Commands:

1. `/recover`  # loads the most recent persisted plan and asks for approval

Keep SIMP manifest updated

Goal: Ensure the project manifest `SIMP.md` reflects current decisions.

Commands:

1. `/simp show`
2. `/simp update <instruction>`  # propose and optionally apply an update

Inspect and heal wiki pages

Goal: Find stale or missing pages and trigger regeneration.

Commands:

1. `/wiki list`
2. `/wiki show <page-id>`
3. `/sync`  # attempts to regenerate stale pages

Use these recipes as templates and adapt file paths and verification commands to your repository.
