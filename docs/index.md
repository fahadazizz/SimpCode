# SimpCode Documentation Portal
# SimpCode Documentation Portal — User-Focused Map

This portal is written for engineers and teams integrating SimpCode into their daily workflows. Use the sections below to find the right materials for your role and intent.

Start here

- New to SimpCode? Read the Getting Started path for installation, onboarding, and a first productive session.
- Evaluating automation risk? Read the Safety and Verification sections in the User Guide and Troubleshooting.
- Integrating into CI or contributing code? See Development and Contributing.

Documentation map (by user intent)

- Getting Started (first-run, install, onboarding)
	- [Overview](getting-started/overview.md)
	- [Installation & Setup](getting-started/setup-and-usage.md)
	- [Installation Deep Dive](getting-started/installation-deep-dive.md)
	- [File Ownership and Permissions](getting-started/file-ownership.md)

- Day-to-day Use (operators and power users)
	- [User Guide / Workflows](guide.md)
	- [How-To Index (task recipes)](how-to/index.md)
	- [Writing Rules & Prompting Guidance](how-to/writing-rules.md)

- Reference (operators and debuggers)
	- [Reference & Command Behaviour](reference/index.md)
	- [Troubleshooting Quick Checks](TROUBLESHOOTING.md)

- Deep Technical Material (engineers, reviewers)
	- [Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)
	- [Comprehensive Guide](COMPREHENSIVE_GUIDE.md)

How to pick what to read

- Beginners: follow the Getting Started sequence top-to-bottom.
- Daily users: skim the Quick Start and keep `Reference` and `Troubleshooting` bookmarked.
- Engineers: read the Architecture Deep Dive and Comprehensive Guide before changing core behavior.

Recommended reading order

1. Getting Started Overview
2. Installation & Setup
3. User Guide (Workflows)
4. How-To Index (task recipes)
5. Reference
6. Architecture Deep Dive

If you find inaccurate or outdated text, please create a small PR or open an issue so documentation and implementation remain in sync.
- CLI and TUI command handlers in `src/simpcode/cli/main.py` and `src/simpcode/cli/shell.py`
