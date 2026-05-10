from pathlib import Path
from typing import List, Dict

class Skill:
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content

class SkillLoader:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.skills_dir = project_root / ".simp" / "skills"

    def load_skills(self) -> List[Skill]:
        skills = []
        if not self.skills_dir.exists():
            return skills
            
        for file in self.skills_dir.glob("*.md"):
            with open(file, "r") as f:
                skills.append(Skill(name=file.stem, content=f.read()))
        return skills
