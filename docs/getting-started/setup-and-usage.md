# Setup and Usage

This page explains the day-to-day use of SimpCode from the moment the TUI opens.

## 1. Enter a Repository

Work from the repository root you want SimpCode to understand.

```bash
cd /path/to/your/project
simp init
```

If the project is not yet onboarded, `simp init` prepares the local project artifacts and then opens the interactive session.

## 2. Learn the Session Header

When the TUI starts, SimpCode shows you the current project, session, provider, and model. Use that as a quick check that you are in the right repository and the correct session.

## 3. Use Slash Commands for Work

The main idea is simple: commands begin with `/`.

### Research

```text
/ask what is the repository structure?
```

Use this when you want an explanation without making changes.

### Plan and Execute

```text
/do add input validation to the user creation workflow
```

This is the main change command. It asks SimpCode to reason about the task, produce a plan, and then execute the change after approval.

You can add flags:

- `--dry-run` shows the plan without applying changes.
- `--yes` skips the approval gate for an approved or trusted run.

### Sync the Wiki

```text
/sync
```

Use this after manual edits, large merges, or any direct repository change that might make the local wiki stale.

### Inspect State

```text
/status
/sessions
/wiki list
/wiki show <page-id>
```

These commands help you understand what SimpCode currently knows and what it has already saved.

### Manage Session Settings

```text
/config
/config --provider anthropic
/config --model claude-3-5-sonnet-latest
```

Use `/config` inside the TUI when you want to inspect or change the active session provider and model.

## 4. Use Plain Text for Conversation

Anything that does not start with `/` is treated as a normal chat turn. That is useful when you want an iterative discussion before you issue a specific command.

Example:

```text
I want to improve the login flow. First explain what the current structure looks like.
```

## 5. Save and Return Later

Use `/exit` when you are done for the moment. SimpCode stores the session locally, so you can come back later and continue from the saved state.

If you need a different saved session, use `/sessions --switch <id>`.

## 6. A Good Daily Workflow

For most projects, this is the most productive order:

1. `/status` to verify you are in the right project
2. `/ask` to understand the area you want to change
3. `/do` with a bounded task
4. review the plan carefully
5. run `/sync` after any manual edits outside SimpCode
6. use `/sessions` if you need to continue in a different thread

## 7. Practical Tips

- keep each command focused on one result
- prefer precise file, module, or behavior references
- use `/dry-run` when you want to inspect the plan first
- use `/ask` before `/do` when the repository is unfamiliar
- sync the wiki whenever the repository changed outside SimpCode

## 8. What a Real Session Feels Like

A real workflow usually looks like this:

```text
/ask where is session state stored?
/do add a better session summary to the sessions list
/status
/sync
/exit
```

That sequence gives you visibility, a bounded change, verification, and a clean exit.
