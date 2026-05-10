# Onboarding

Starting a new project with SimpCode is a straightforward process.

## 1. Installation
SimpCode should be installed in your environment (preferably a virtual environment).
```bash
pip install -e .
```

## 2. Initialization
Run the `init` command from the root of your project.
```bash
simp init
```
This command performs the following:
- Analyzes your project structure.
- Detects your tech stack (e.g., Python, Node.js).
- Creates `SIMP.md` (Project Intelligence).
- Creates `AGENT.md` (Behavioral Rules).

## 3. Configuring Constraints
Review and modify the generated files:
- **`SIMP.md`**: Ensure the test and lint commands are correct.
- **`AGENT.md`**: Add any project-specific rules or invariants the assistant must follow.

## 4. Building the Initial Wiki
Currently, SimpCode relies on its internal analysis and user interaction to build the Wiki. As you perform tasks with `simp do`, the Wiki will grow and become more refined. You can also manually create pages in `.simp/wiki/` to capture critical architectural knowledge.
