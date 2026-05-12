# SimpCode Documentation

This documentation set explains the current **TUI-first** SimpCode experience from a real user’s point of view.

The goal of SimpCode is simple: help you understand a repository, plan work safely, make changes with verification, and keep a local project memory in sync as the codebase evolves.

## Start Here

If you are new to SimpCode, read these in order:

1. [User Guide](guide.md)
2. [Getting Started Overview](getting-started/overview.md)
3. [Setup and Usage](getting-started/setup-and-usage.md)
4. [Command Reference](reference/index.md)

## Documentation Map

### Getting Started

- [Overview](getting-started/overview.md)
- [Installation Deep Dive](getting-started/installation-deep-dive.md)
- [Setup and Usage](getting-started/setup-and-usage.md)
- [File Ownership](getting-started/file-ownership.md)

### Concepts

- [Concepts Overview](concepts/index.md)
- [Current Architecture](concepts/architecture.md)

### How To

- [How To Overview](how-to/index.md)
- [Advanced Capabilities](how-to/advanced-capabilities.md)
- [Writing Rules](how-to/writing-rules.md)

### Reference

- [Command and File Reference](reference/index.md)
- [Troubleshooting](TROUBLESHOOTING.md)

### Examples

- [Real-World Examples](EXAMPLES.md)

## What SimpCode Is Best For

- onboarding a real repository into a local, inspectable workflow
- asking questions about a codebase without making changes
- planning multi-step engineering work before editing
- running bounded implementation tasks with verification
- keeping session history and project memory available between runs
- refreshing local wiki state after manual edits or merges

## What SimpCode Is Not

SimpCode is not a general-purpose shell replacement, and it is not designed for free-form command execution from the main user interface. The current model is intentionally focused: enter the interactive session, use slash commands for work, and let the workflow layer manage the project artifacts and execution flow.

## Key Files in a Project

- `SIMP.md`: the current project manifest and visible project snapshot.
- `SPEC.md`: optional target-state requirements and constraints.
- `.simp/wiki/`: the project knowledge base.
- `.simp/sessions/`: saved session state.
- `.simp/plans/`: persisted task plans.

## Quick Decision Guide

| If you want to... | Read this |
|---|---|
| Install or configure SimpCode | [Getting Started Overview](getting-started/overview.md) |
| Learn the full workflow | [User Guide](guide.md) |
| Understand the current architecture | [Current Architecture](concepts/architecture.md) |
| Find a command or file path | [Reference](reference/index.md) |
| Solve a runtime problem | [Troubleshooting](TROUBLESHOOTING.md) |
| See a practical scenario | [Examples](EXAMPLES.md) |

## Documentation Philosophy

This documentation is written for real usage:

- it explains the user flow before the internals
- it assumes the current TUI-first architecture
- it avoids legacy implementation language
- it focuses on what to do, what SimpCode stores, and how to use it well on a real project

| Feature | Details |
|---------|---------|
| **Wiki-First** | Semantic knowledge persists across sessions |
| **Safe Execution** | Strict scope enforcement, permission checks, verification |
| **Intelligent Context** | Tiered assembly maximizes value per token |
| **Continuous Learning** | System improves with each task |
| **Multi-Provider** | Works with Anthropic, OpenAI, Groq, Google, OLLama |
| **Production Ready** | All 8 flaws fixed, 25/25 tests passing |

---

## 🎓 Learning Path

**Recommended reading order**:

1. **[Comprehensive Guide - What is SimpCode](COMPREHENSIVE_GUIDE.md#what-is-simpcode)** (5 min)
   - Understand the problem and solution

2. **[Getting Started](COMPREHENSIVE_GUIDE.md#getting-started)** (10 min)
   - Install and set up

3. **[Core Concepts](COMPREHENSIVE_GUIDE.md#core-concepts)** (15 min)
   - Understand SPEC, SIMP, Wiki, workflow

4. **[Examples 1-2](EXAMPLES.md)** (15 min)
   - See it in action

5. **[User Workflows](COMPREHENSIVE_GUIDE.md#user-workflows)** (10 min)
   - Learn how to work with SimpCode

6. **[Advanced Usage](COMPREHENSIVE_GUIDE.md#advanced-usage)** (20 min)
   - Scale to larger projects

7. **[Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)** (30 min)
   - Understand internals (optional for users)

**Total time**: ~90 minutes to full understanding

---

## 📞 Support

### Having Issues?
1. Check [Troubleshooting Quick Reference](TROUBLESHOOTING.md#quick-reference)
2. Browse [Specific Issues](TROUBLESHOOTING.md)
3. Try [Debugging Techniques](TROUBLESHOOTING.md#debugging-techniques)

### Questions?
1. Check [FAQ](COMPREHENSIVE_GUIDE.md#faq)
2. Review [Examples](EXAMPLES.md)
3. Read [Documentation](COMPREHENSIVE_GUIDE.md)

### Want to Contribute?
1. Read [Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)
2. Check [Extension Points](ARCHITECTURE_DEEP_DIVE.md#extension-points)
3. Open an issue on GitHub

---

**Last Updated**: 2026-05-12 | SimpCode v3.0 | Production Ready ✓

For the complete user experience: Start with [Comprehensive Guide](COMPREHENSIVE_GUIDE.md)
