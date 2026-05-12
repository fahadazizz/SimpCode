# SimpCode User Guide

This is the canonical guide for using SimpCode in real projects.

SimpCode is a task-oriented engineering assistant that does not rely on a single chat thread. It builds a semantic model of your repository, plans work before editing, verifies changes after every write, and continuously refreshes its understanding as the codebase changes.

## What SimpCode Is Good At

- understanding large or unfamiliar repositories
- planning multi-step engineering work before making edits
- applying changes with verification gates
- remembering project structure through the Wiki
- staying aligned with your project requirements while you work

## The Core Mental Model

SimpCode works with four layers of information:

### 1. `SPEC.md` - what you want to build
This is the authoritative project requirement file.

Use it for:
- product goals
- architecture intent
- constraints and non-negotiables
- performance, reliability, and security requirements
- scope boundaries and success criteria

Write `SPEC.md` when you want SimpCode to optimize toward a target state rather than only describe the current repository.

### 2. `SIMP.md` - the project manifest
This is the project-facing overview document.

Use it for:
- the current project identity
- architecture summary
- major modules and responsibilities
- implementation notes that should stay visible during work

In SimpCode, `SIMP.md` is the high-level companion to `SPEC.md`. Keep it readable, current, and concise.

### 3. `.simp/wiki/` - the semantic knowledge base
This is the system-managed memory layer.

It stores:
- module summaries
- code relationships
- learned patterns
- risks and invariants
- staleness-aware source references

You do not manually maintain the Wiki. SimpCode updates it as part of its indexing and learning loop.

### 4. `src/simpcode/core/prompts/` - internal system prompts
These are SimpCode's internal reasoning assets.

They are not project docs and are not meant to be edited as part of normal project onboarding. If you are customizing SimpCode itself, these prompts matter; if you are using SimpCode on your own project, focus on `SPEC.md`, `SIMP.md`, and the Wiki.

## How the System Works

### 1. Onboarding
When you run `simp init`, SimpCode:

1. scans the repository structure
2. builds `SIMP.md` and `SPEC.md`
3. bootstraps the semantic Wiki
4. indexes module relationships and useful entry points
5. enters the interactive shell

### 2. Research (`simp ask`)
When you ask a question, SimpCode:

1. loads the project context
2. navigates the Wiki first
3. reads targeted source snippets when needed
4. answers based on the actual codebase, not guesses

Use `ask` when you want to understand the repository without changing it.

### 3. Planning and Execution (`simp do`)
When you request a task, SimpCode:

1. scans the repository context
2. generates a structured implementation plan
3. asks for approval unless you explicitly skip it
4. executes the plan step by step
5. verifies each write immediately
6. updates the Wiki after changes

Use `do` when you want SimpCode to modify code safely and systematically.

### 4. Syncing (`simp sync`)
If you or your team make manual changes outside SimpCode, run `simp sync` so the Wiki can catch up with the new reality on disk.

## Setup

### Prerequisites
- Python 3.12 or newer
- Git
- an API key for at least one supported LLM provider

### Install
If you are contributing locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Configure
Run:

```bash
simp setup
```

Choose a provider, model, and API key. Your config is stored locally in your SimpCode config directory.

### Initialize a project
From the repository you want SimpCode to work on:

```bash
simp init
```

That creates the project intelligence files and the semantic Wiki.

## How to Use SimpCode Well on Real Projects

### Write a strong `SPEC.md`
A good `SPEC.md` is the biggest quality multiplier.

Include:
- business goals
- the problem being solved
- architecture boundaries
- allowed and disallowed changes
- scalability and reliability targets
- success metrics

Keep it specific. The more concrete the specification, the better SimpCode can reason about tradeoffs.

### Keep `SIMP.md` readable
Treat `SIMP.md` as the project overview, not a giant dump of every detail.

Good content:
- a short identity section
- architecture summary
- module responsibilities
- important entry points
- operational notes

Avoid turning it into a second specification file.

### Review every plan
SimpCode is safest when you inspect the generated plan before execution.

Check:
- whether the target files are correct
- whether the verification step is meaningful
- whether the scope is too broad
- whether the task should be broken into smaller steps

### Use explicit file and module references
The more precise your task, the better the result.

Good:
- "Add retry logic in `src/simpcode/harness/tools.py`"
- "Update the planning flow to include `SPEC.md` requirements"
- "Refactor the Wiki bootstrap to support project-specific skills"

Weak:
- "Make it better"
- "Fix the architecture"

### Keep the Wiki fresh
Run `simp sync` when:
- you change many files manually
- you merge a large branch
- SimpCode appears to be reasoning from stale context

### Use skills when a project needs specialized behavior
SimpCode can load project-specific or global skills from the configured skills directories.

Use skills for:
- special workflows
- domain-specific formatting
- language-specific conventions
- repeatable project practices

## How to Make SimpCode More Productive on Complex Projects

### 1. Start with a precise SPEC
Large projects fail when requirements are vague.

Good SPEC content includes:
- architecture goals
- data flow expectations
- module ownership
- external integrations
- testing and deployment constraints

### 2. Split large work into focused missions
If the task touches many files or subsystems, break it into smaller missions.

This keeps plans safer, context smaller, and verification more reliable.

### 3. Keep a tight approval loop
Approve only plans that are:
- bounded
- testable
- scoped to the actual requirement
- measurable

### 4. Use the Wiki as a reality check
When SimpCode says something about the repository, trust the Wiki-backed answer over a vague memory.

### 5. Treat `SIMP.md` as a communication layer
It helps SimpCode and humans stay aligned on what the repository is and how it is structured.

### 6. Treat internal prompts as implementation details
If you are using SimpCode as a tool on your own project, the prompt files are not something you normally edit.

If you are extending SimpCode itself, then the prompt folder becomes part of the framework codebase and should be maintained with the same discipline as the rest of the runtime.

## Common Workflows

### New repository onboarding
1. create `SPEC.md`
2. run `simp init`
3. review the generated `SIMP.md`
4. inspect the initial Wiki pages
5. run `simp ask` on a structural question
6. try a small `simp do` task

### Feature work
1. update `SPEC.md` if the feature changes the target architecture
2. ask SimpCode to research relevant modules
3. review the generated plan
4. execute the plan in small steps
5. run `simp sync` if you changed files manually

### Refactoring a large module
1. write down the desired result in `SPEC.md`
2. ask for a plan that isolates the affected files
3. approve a narrow scope
4. verify after each write
5. use `simp sync` after the refactor if needed

## Troubleshooting

### SimpCode seems to miss recent changes
- run `simp sync`
- confirm the files were actually saved
- check whether the Wiki page is stale

### The plan is too broad
- clarify the SPEC
- break the task into smaller steps
- point to exact files or modules

### The task feels under-specified
- add more detail to `SPEC.md`
- include exact acceptance criteria
- define the non-negotiables up front

### A prompt mentions `AGENT.md`
- treat that as legacy documentation from an older architecture
- for the current repository flow, prioritize `SPEC.md`, `SIMP.md`, and the Wiki

## Recommended Real-World Operating Pattern

For complex projects, the best SimpCode loop is:

1. keep `SPEC.md` sharp
2. keep `SIMP.md` concise and accurate
3. let the Wiki carry the current code reality
4. review plans before execution
5. verify every write
6. sync when you make manual changes
7. use skills for domain-specific repetition

If you do those things, SimpCode becomes much more reliable on large, evolving codebases.
