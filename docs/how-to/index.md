# How-to Guides

Step-by-step recipes for mastering SimpCode in your daily development lifecycle.

---

## Implementing a New Feature (`simp do`)

The `do` command is for when you have a specific objective and want SimpCode to handle the implementation.

### Best Practices:
1.  **Be Explicit about Location**: If you know where the code should go, tell the AI.
    *   *Bad*: "Add authentication."
    *   *Good*: "Implement OAuth2 logic in `src/auth.py` using the `jose` library."
2.  **Use Contextual Hints**: Mention existing functions or patterns to ensure consistency.
    *   "Follow the pattern used in `src/models/user.py` for this new entity."
3.  **Review the Plan**: Look for unexpected deletions or weird patterns in the proposed changes.

---

## Researching Complex Logic (`simp ask`)

Use `ask` for architectural discovery without making changes.

### Example Scenarios:
- **Tracing Flow**: "Trace the lifecycle of a request from the middleware to the database."
- **Finding Bottlenecks**: "Identify potential performance issues in the current hash calculation logic."
- **Dependency Map**: "Which modules would be affected if I renamed the `State` class?"

---

## Writing a Strong `SPEC.md`

Every project needs a clear target state. Put that in `SPEC.md` so SimpCode knows what success looks like.

### Good `SPEC.md` content:
- **Architecture Goals**: What shape should the system have?
- **Constraints**: What must never change?
- **Acceptance Criteria**: How do we know the task is done?
- **Quality Targets**: Performance, security, reliability, and scalability goals.
- **Scope Boundaries**: What is explicitly out of scope?

For the full workflow and real-world examples, read the [SimpCode User Guide](../guide.md).
---

## Keeping Knowledge Fresh (`simp sync`)

If you or your team make significant manual changes to the codebase, the Wiki can become stale.

### When to run `sync`:
- after a `git pull`
- after manually deleting files
- before starting a large multi-file `do` task

Running `simp sync` forces a re-index of the repository so the AI's mental model matches the reality on disk.

---

## Interactive Pairing (`simp chat`)

Sometimes, a single command isn't enough. The `chat` command launches an interactive TUI (Terminal User Interface).

### What can you do in Chat?
- **Iterative Debugging**: Discuss a bug, let the AI suggest a fix, approve it, and then discuss the results.
- **Brainstorming**: Ask questions like "What's the best way to structure this new module?" and see code examples in the markdown-rendered output.
- **Multitasking**: Run multiple research questions back-to-back without restarting the CLI.

---

## Global Model Hotswapping

You don't have to stick to one model. Use the dynamic flags for specific tasks.

- **For brainstorming (fast/cheap)**:
  `simp chat --provider groq --model llama-3.1-70b-versatile`
- **For complex refactoring (high reasoning)**:
  `simp do "Refactor state machine" --provider anthropic --model claude-3-5-sonnet-latest`
