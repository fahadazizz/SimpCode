from pathlib import Path
from simpcode.core.analyzer import ProjectInfo

class DocumentGenerator:
    def __init__(self, root: Path):
        self.root = root

    def generate_simp_md(self, info: ProjectInfo):
        content = f"""# SIMP.md — Project Intelligence

## Overview
- **Project Name:** {info.name}
- **Tech Stack:** {", ".join(info.stack)}
- **Entry Points:** {", ".join(info.entry_points)}

## Verification
- **Test Command:** {", ".join(info.test_commands)}
- **Lint Command:** {", ".join(info.lint_commands)}

## Structure
{chr(10).join(f"- {s}" for s in info.structure)}
"""
        with open(self.root / "SIMP.md", "w") as f:
            f.write(content)

    def generate_agent_md(self, info: ProjectInfo):
        content = """# AGENT.md — Behavioral Rules

## Reasoning
- Always consult the Wiki before reading code.
- Decompose tasks into a step-by-step plan.
- Identify invariants and risks before proposing changes.

## Execution
- Validate each step with linting and tests.
- Update Wiki hashes immediately after file writes.
- Never write to files outside the approved plan scope.
"""
        with open(self.root / "AGENT.md", "w") as f:
            f.write(content)
