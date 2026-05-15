# How-To Guides

Use this section for task-focused instructions.

## Guides

- [Advanced Capabilities](advanced-capabilities.md)
- [Writing Rules and Prompting Guidance](writing-rules.md)

## Most Common How-To Tasks

### Run a safe implementation cycle

1. `/status`
2. `/do <task> --dry-run`
3. review plan
4. `/do <task>`
5. `/sync`
6. `/status`

### Resume interrupted work

1. `/sessions`
2. `/sessions --switch <id>` or `/recover`

### Keep manifests aligned

1. `/simp show`
2. `/simp update <instruction>`

### Inspect wiki reliability

1. `/wiki list`
2. `/wiki show <page-id>`
3. `/sync` for stale pages
