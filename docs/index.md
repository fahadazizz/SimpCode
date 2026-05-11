# SimpCode Documentation

Welcome to the official documentation for **SimpCode**, the high-integrity engineering assistant designed to automate complex coding tasks while maintaining architectural absolute truth.

Unlike chat-based assistants that prioritize conversation, SimpCode is a **task-oriented orchestrator**. It builds a persistent mental model of your codebase, plans its actions before execution, and verifies every change against your project's unique constraints.

---

##  How to use these docs

Our documentation is organized following the **Diátaxis framework** to help you find exactly what you need based on your current goal.

### [Getting Started](getting-started/overview.md)
*Learning-oriented for newcomers.*
Start here to install SimpCode globally, configure your first LLM provider, and run your first successful "Mission" on a codebase.

### [How-to Guides](how-to/index.md)
*Problem-oriented for active users.*
Step-by-step recipes for common real-world scenarios: implementing features, refactoring legacy modules, managing large context budgets, and customizing your AI agent's behavior.

### [Concepts & Architecture](concepts/index.md)
*Understanding-oriented for experts.*
Deep dives into the "Why" behind SimpCode. Learn about the **Semantic Wiki**, the **ReAct Engineering Loop**, the **Hardened Execution Harness**, and how SimpCode avoids context poisoning.

### [Reference](reference/index.md)
*Information-oriented for quick lookups.*
Technical specifications for every CLI flag, environment variable, configuration key, and internal prompt template.

---

## Why SimpCode?

The modern developer's bottleneck isn't typing speed—it's **context management**. As projects grow, AI assistants often lose the "big picture," leading to regressions and "spaghetti code."

SimpCode solves this through three core pillars:

1.  **The Semantic Wiki**: A repository-local knowledge base that persists across sessions, mapping architectural intent to file reality.
2.  **Explicit Planning**: SimpCode never writes code without first presenting a human-readable "Implementation Plan" for your approval.
3.  **Policy-Driven Action**: Through `AGENT.md`, you define the immutable rules of your project. SimpCode treats these as first-class constraints, not just suggestions.

---

> "SimpCode isn't just an assistant; it's a junior engineer who never sleeps, remembers every function you've ever written, and follows your style guide to the letter."
