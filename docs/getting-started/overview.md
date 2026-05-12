# Getting Started with SimpCode

This guide will take you from installation to your first successful automated task. Whether you're a solo developer or part of a large engineering team, SimpCode is designed to integrate seamlessly into your existing workflow.

---

## Prerequisites

Before you begin, ensure your system meets the following requirements:

- **OS**: macOS, Linux, or Windows (via WSL2).
- **Python**: Version 3.10 or higher.
- **Git**: Installed and configured in your shell.
- **LLM API Key**: Access to at least one supported provider (Anthropic, OpenAI, Groq, Google, etc.).

---

## ⚡ Quick Start: The One-Liner

For most users, our automated installation script is the fastest way to get SimpCode running globally. This script clones the repository to a protected local directory, sets up a virtual environment, and symlinks the `simp` command to your path.

```bash
curl -sSL https://raw.githubusercontent.com/fahadazizz/simpcode/main/install.sh | bash
```

*Note: After running this, restart your terminal or source your profile to ensure `~/.local/bin` is in your PATH.*

---

## Step 1: Global Configuration

SimpCode needs to know which AI "brain" to use and how to authenticate. Run the setup wizard:

```bash
simp setup
```

The wizard will guide you through:
1.  **Selecting a Provider**: Choose your preferred LLM engine.
2.  **Model Identification**: Enter the specific model ID (e.g., `claude-3-5-sonnet-latest`).
3.  **Authentication**: Securely input your API Key.
4.  **Verification**: SimpCode will perform a handshake to ensure the connection is live.

**Where is this kept?**
Your configuration is stored locally at `~/.simpcode/config.json`. This file is never shared or uploaded; it remains on your machine as a secure global credential.

---

## Step 2: Project Onboarding (`init`)

SimpCode doesn't start guessing. It requires a formal onboarding phase for every repository you work in. That phase builds the initial semantic model that lets the AI understand the project structure and start reasoning from real source files.

Navigate to your target project folder and run:

```bash
simp init
```

### What happens during initialization?
- **Structural Audit**: SimpCode scans your directory tree to understand module relationships.
- **Specification Layer (`SPEC.md`)**: The target-state requirements for the project are created or refreshed.
- **Project Manifest (`SIMP.md`)**: A high-level overview of the project is generated.
- **Knowledge Bootstrap**: The first nodes of the semantic Wiki are created in `.simp/wiki/`.

For a full explanation of the architecture and the user workflow, read the [SimpCode User Guide](../guide.md).

---

## Step 3: Your First Mission

Now that SimpCode is "aware" of your code, you can give it a task. Let's try a research task first to test its knowledge.

```bash
simp ask "Explain how the main entry point of this project is structured."
```

SimpCode will navigate its Wiki, locate the relevant files, and provide a deep architectural explanation based on **actual code**, not just generic AI guesses.

### Moving to Action
Once you trust the research, try a modification:

```bash
simp do "Add a new utility function to calculate file hashes in src/utils.py"
```

1.  **Plan**: SimpCode will present an **Implementation Plan**.
2.  **Review**: Read the plan. It will tell you exactly which lines it intends to change.
3.  **Approve**: Type `y` or `yes`.
4.  **Verify**: Watch as SimpCode writes the code and checks for syntax errors.

---

## Next Steps

- **[File Ownership](file-ownership.md)**: Understand which files you should edit and which belong to SimpCode.
- **Master the Shell**: Use `simp chat` for a persistent pair-programming session.
- **Write a Strong SPEC**: Learn how to define project requirements in the [SimpCode User Guide](../guide.md).
- **Deep Dive**: Understand the [Semantic Wiki architecture](../concepts/index.md#the-semantic-wiki) to maximize accuracy.
