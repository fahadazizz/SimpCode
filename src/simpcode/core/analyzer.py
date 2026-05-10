import os
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel

class ProjectInfo(BaseModel):
    name: str
    stack: List[str]
    entry_points: List[str]
    test_commands: List[str]
    lint_commands: List[str]
    structure: List[str]

class ProjectAnalyzer:
    def __init__(self, root: Path):
        self.root = root

    def analyze(self) -> ProjectInfo:
        stack = []
        entry_points = []
        test_commands = []
        lint_commands = []
        
        # Detect Python
        if (self.root / "pyproject.toml").exists() or (self.root / "requirements.txt").exists():
            stack.append("Python")
            if (self.root / "pytest.ini").exists() or (self.root / "tests").exists():
                test_commands.append("pytest")
            else:
                test_commands.append("python -m unittest")
            lint_commands.append("flake8")
            
        # Detect Node.js
        if (self.root / "package.json").exists():
            stack.append("Node.js")
            test_commands.append("npm test")
            lint_commands.append("npm run lint")

        # Basic entry point detection (common names)
        potential_entries = ["main.py", "app.py", "index.js", "src/main.py", "src/index.ts"]
        for p in potential_entries:
            if (self.root / p).exists():
                entry_points.append(p)

        # Basic structure
        structure = [str(p.relative_to(self.root)) for p in self.root.iterdir() if not p.name.startswith(".")]

        return ProjectInfo(
            name=self.root.name,
            stack=stack,
            entry_points=entry_points,
            test_commands=test_commands,
            lint_commands=lint_commands,
            structure=structure
        )
