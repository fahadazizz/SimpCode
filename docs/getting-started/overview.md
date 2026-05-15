# Getting Started Overview

This overview gives you the shortest reliable path to productive SimpCode usage.

If you are onboarding for the first time, read this page first, then move to:

- [Installation Deep Dive](installation-deep-dive.md)
- [Setup and Usage](setup-and-usage.md)
- [File Ownership](file-ownership.md)

## 1. What You Need Before Starting

- Python 3.12+
- a local repository you want to work on
- network access for your chosen LLM provider (unless using local Ollama)

## 2. Fast Path

From your repository:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

simp setup
simp init
```

Then inside TUI:

```text
/help
/status
/ask what does this repository do?
```

## 3. What Happens After `simp init`

SimpCode verifies onboarding artifacts and creates missing pieces.

Core outputs include:

- `SIMP.md`
- `SPEC.md`
- `.simp/wiki/` structure and core pages

You can inspect those files directly after init.

## 4. Your Daily Command Set

Most users only need:

- `/ask`
- `/do`
- `/status`
- `/sync`
- `/wiki list`
- `/sessions`

## 5. Minimal Operational Habit

Use this sequence before and after major work:

```text
/status
/do <task> --dry-run
/do <task>
/sync
/status
```

This keeps risk and context drift under control.
