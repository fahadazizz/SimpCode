# Getting Started Overview

This page gives you the shortest path from “I have a repository” to “I am using SimpCode on it correctly.”

## The Short Version

1. install SimpCode into a Python environment
2. run `simp setup` once to configure your provider
3. run `simp init` inside the repository you want to work on
4. use the interactive TUI for all research and implementation work

That is the default operating model.

## What You Need

- Python 3.10 or newer
- Git
- a supported LLM provider and API key, unless you are using a local model endpoint
- a repository you actually want to work on

## The First Two Commands

### `simp setup`

Use this when you need to define the provider and model for your local SimpCode installation.

This is global configuration. You typically do it once and then reuse it across repositories.

### `simp init`

Use this inside a project repository.

It prepares the project artifacts and then opens the TUI so you can begin working immediately.

If the repository has not been onboarded before, `simp init` creates the local project memory and the initial wiki. If the project already exists in SimpCode, it refreshes the onboarding state and then lets you continue.

## What the TUI Is For

The TUI is where you do the actual work:

- ask questions about the repository
- request implementation plans
- approve bounded changes
- inspect wiki pages
- review session state
- sync the local project memory after manual edits

The TUI is also where SimpCode keeps session continuity. When you return to a repository later, you can pick up from a saved session rather than starting from nothing.

## The Main User Flow

After initialization, a typical flow looks like this:

1. ask a question to understand the repository
2. use `/do` for a concrete change
3. review the generated plan before approving it
4. sync the wiki after manual repository changes
5. inspect sessions if you need to continue later

## Recommended First Task

If you want to see whether SimpCode understands a repository, begin with a research question:

```text
/ask what is the main entry point and how is the project organized?
```

That gives you a low-risk check of the repository knowledge before you ask it to edit anything.

## Recommended First Change

Once research looks correct, request a small bounded edit:

```text
/do add input validation to the user creation path
```

Start small. SimpCode is strongest when the task is clear, scoped, and easy to verify.

## What to Read Next

- [Installation Deep Dive](installation-deep-dive.md)
- [Setup and Usage](setup-and-usage.md)
- [File Ownership](file-ownership.md)
- [User Guide](../guide.md)
- [Command Reference](../reference/index.md)
