# Getting Started: Setup and Core Usage

This guide covers everything required to deploy SimpCode within an active repository and explains how to begin engineering tasks organically.

---

## 1. Setup & Installation

Ensure you have a modern Python environment active (e.g. `pyenv` or `venv` mapping to python 3.10+).

```bash
# Enter the root of your target project
cd /your/complex/project

# Launch SimpCode using the CLI module
python -m simpcode.cli.main
```
*(Optionally you can map this to an alias `simp` in your `~/.zshrc` profile for quick terminal access.)*

## 2. Onboarding an Existing Project
The moment you enter a project that SimpCode hasn't seen natively, run:
```
simp> /init
```
**What happens under the hood?**
SimpCode will run a structural deep-sweep of your codebase (supporting Rust, Go, Python, TS/JS, and legacy enterprise layouts out-of-the-box). It parses thousands of files, compressing tree topography automatically to maintain a strict memory budget context. It then initializes the persistent `.simp/` directory and the project documents that drive the workflow: `SIMP.md` and the Wiki. (`SPEC.md` may also be created as an optional project requirements file if a contract-like spec is detected or requested.)

## 3. The Core Developer Workflow

### Exploring your Codebase (`/ask`)
For discovery and documentation tasks without editing, use the standard prompt command.
```
simp> /ask Explain exactly how the authentication module communicates with the database layer.
```
SimpCode consults the semantic wiki and targets related source nodes to output deeply contextualized architecture definitions.

### The Engineering Loop (`/do`)
The `/do` command is the main powerhouse. This invokes the full Planning & ReAct Executor loop.
```
simp> /do Create a new robust error handling middleware and ensure that the legacy API paths import it seamlessly. 
```

**Understanding the Execution phases:**
1. **Intelligence Scan:** The console status will say "Scanning scene...". It pulls relevant architectural files.
2. **Planning Verification:** It constructs a multi-step objective action plan and will prompt you (Y/n). You can easily pass `--yes` directly in the command. You can also run `--dry-run` to watch the execution trace without touching a file.
3. **Execution Pipeline:** It visually streams the `[Plan] -> [Thought] -> [Action]` loop live within the terminal utilizing formatting, so you see exactly what terminal commands it runs and precisely which lines it replaces.

### Syncing (`/sync`)
Because the system runs dynamic self-healing node architectures, synchronization overhead is nearly zero. However, if you natively execute massive file restructuring or multi-file Git checkouts away from the TUI, manually correct it by running:
```
simp> /sync
```
This forces the internal Wiki Engine to discard broken hash references globally.

### Managing System Memory (`/clear` and `/sessions`)
SimpCode maintains historical TUI sessions dynamically. If your console starts feeling slow or confused by too much scattered conversation context, issue:
```
simp> /clear
```
To load previous historical engineering loops:
```
simp> /sessions
```
This enables branching complex iterations elegantly over days.
