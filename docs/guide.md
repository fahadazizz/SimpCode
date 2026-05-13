# SimpCode User Guide

This is the canonical user guide for the current SimpCode experience.

The important idea is straightforward: SimpCode is not a chat box with code completion. It is a local, project-aware engineering workflow that starts by learning your repository, then lets you research, plan, execute, and recover from inside a persistent terminal session.

## Who This Guide Is For

- developers onboarding a real repository into SimpCode
- contributors who want the current workflow described clearly
- teams that want predictable, reviewable terminal-based assistance
- anyone who wants to know how to use the TUI well on a real project

## The User Journey

The normal flow looks like this:

1. install SimpCode into a Python environment
2. configure a provider once with `simp setup`
3. initialize a repository with `simp init`
4. continue inside the TUI using slash commands
5. save or return to sessions later if needed
6. refresh the wiki after manual repository changes

That is the user-facing model. The rest of the guide explains why it works and how to use it well.

## What SimpCode Actually Does

At a high level, SimpCode:

- reads the current repository and project metadata
- keeps a local semantic wiki for project knowledge
- uses `SIMP.md` and optional `SPEC.md` to stay aligned with your intent
- assembles focused context instead of dumping the entire repository into the model
- generates a plan before making changes
- saves the task output and session state locally
- refreshes the wiki when the repository changes

## The Core Files

SimpCode uses a small set of local project artifacts:

- `SIMP.md` is the visible project manifest.
- `SPEC.md` is the optional target-state specification.
- `.simp/wiki/` stores the project knowledge base.
- `.simp/sessions/` stores saved TUI sessions.
- `.simp/plans/` stores persisted task plans.

If you remember only one thing: the project artifacts live in your repository, not in a remote SimpCode account.

## Installation and First Launch

You can use SimpCode from a local development checkout or from an installed package. For the local repository in this workspace, the simplest path is:

```bash
cd /Volumes/DataDrive/SimpCode
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then configure your provider:

```bash
simp setup
```

After setup, go to the repository you want SimpCode to work on and run:

```bash
simp init
```

`simp init` prepares the repository and then opens the interactive shell.

## What Happens During Onboarding

When you run `simp init`, SimpCode:

1. identifies the repository root
2. collects project metadata
3. writes or refreshes `SIMP.md`
4. writes `SPEC.md` if the onboarding output includes specification content
5. creates the `.simp/wiki/` index and initial knowledge base
6. opens the TUI so you can start working immediately

If a project is already onboarded, `simp init` behaves as a refresh entry point and takes you back into the interactive workflow.

## How the TUI Works

The TUI is the main interface now.

- Type a slash command to perform a structured action.
- Type regular text to start a normal chat turn.
- Use `/help` if you need the command list.
- Use `/exit` to save the current session and quit.

The shell is intentionally simple. It is not trying to be a desktop application. It is a focused terminal workspace for project reasoning and implementation.

### The Main Command Pattern

This is the recommended shape:

```text
/ask what does the auth layer currently do?
/do add input validation for the user API --dry-run
/status
/wiki list
/sessions
```

Anything that does not begin with `/` is treated as a regular chat turn and runs through the current session context.

## Working Modes

### Research Mode

Use `/ask` when you want a technical explanation or a repository question answered without making changes.

Examples:

```text
/ask where is session state persisted?
/ask how does the wiki stay in sync?
/ask which files define the public command interface?
```

This mode is useful when you want to learn the current shape of the codebase before taking action.

### Task Mode

Use `/do` when you want SimpCode to plan and execute a bounded change.

Examples:

```text
/do add a retry strategy for provider failures
/do refactor the command parsing to be easier to test --dry-run
/do update the session list output to show more useful previews --yes
```

Task mode is the safest place to ask for code changes because it starts from context, generates a plan, and persists the result.

### Maintenance Mode

Use maintenance commands when the repository changed outside SimpCode or when you need to inspect the current state.

- `/sync` refreshes wiki knowledge after manual edits or big merges.
- `/status` shows the repository and wiki health summary.
- `/recover` loads the latest recoverable plan artifact.
- `/sessions` shows saved sessions and lets you switch between them.

## Project Planning and Execution

The workflow layer uses a predictable structure:

1. collect repository context
2. assemble the most relevant wiki and source snippets
3. generate a plan for the requested task
4. ask for approval unless you explicitly skip it
5. execute the plan step by step
6. save the plan and session state locally
7. update the wiki and local knowledge after the task

This is why SimpCode feels different from a normal chat assistant. It is not only answering; it is operating inside a project lifecycle.

## How to Use `SPEC.md`

`SPEC.md` is optional, but it is powerful.

Use it when you want SimpCode to optimize toward an explicit target state:

- product requirements
- constraints that should not be broken
- architecture boundaries
- acceptance criteria
- testing and quality expectations

If your repository has a clear direction, `SPEC.md` should describe the destination in language a human reviewer would approve.

### Good `SPEC.md` content

- what the system should do
- what the system must not do
- what must remain stable during the change
- what counts as complete
- what must be verified afterward

### Bad `SPEC.md` content

- vague goals with no acceptance criteria
- one-off task instructions that belong in a slash command
- internal implementation details that are not actually project requirements

## How to Use `SIMP.md`

`SIMP.md` should stay readable and useful to a human. Think of it as the project snapshot SimpCode and your team can refer to while working.

Strong `SIMP.md` entries usually include:

- repository purpose
- major folders and their responsibilities
- important conventions
- entry points and operational notes
- any current constraints the team should remember

Do not treat it as a log dump. It should be concise enough that someone can actually use it.

## Sessions and Recovery

SimpCode keeps sessions locally so you can return to work later.

- `/sessions` shows saved sessions.
- `/sessions --switch <id>` loads another session.
- `/recover` reloads the most recent persisted plan when you need to continue from a previous task.

This is especially useful when you are working on a multi-step repository change over more than one sitting.

## Best Practices That Matter

### Be specific

The more precise your request, the better the result.

Good:

```text
/do add a provider-aware status display to the interactive shell
```

Less useful:

```text
/do make it better
```

### Keep tasks bounded

Try to request one meaningful change at a time. Large tasks are fine, but they should still have a clear end point.

### Use the wiki as a sanity check

When you are not sure how the repository is structured, ask first. The research path exists to reduce wrong edits.

### Sync after manual changes

If you changed files directly, run `/sync` before asking SimpCode for a new task. That keeps the local knowledge consistent with the code on disk.

### Review plans before approving

The generated plan is your chance to catch scope problems early. If the plan is too wide, narrow the task and try again.

## When SimpCode Works Best

SimpCode is strongest when the repository is:

- real enough to have structure
- large enough that context matters
- stable enough that local memory is useful
- worked on repeatedly over time

That is exactly the sort of environment where a persistent project memory pays off.

## When to Stop and Reframe

If you notice that a task description is too broad, split it into separate slash commands. If you are missing requirements, write them into `SPEC.md` first. If the repository changed outside SimpCode, sync before continuing.

## What to Read Next

- [Getting Started Overview](getting-started/overview.md)
- [Current Architecture](concepts/architecture.md)
- [Command Reference](reference/index.md)
- [Examples](EXAMPLES.md)
- [Troubleshooting](TROUBLESHOOTING.md)
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
