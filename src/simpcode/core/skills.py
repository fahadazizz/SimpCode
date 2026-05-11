import yaml
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
import os

class SkillMetadata(BaseModel):
    id: str
    description: str

class Skill(BaseModel):
    metadata: SkillMetadata
    content: str
    
    @classmethod
    def from_file(cls, file_path: Path) -> "Skill":
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
        if not raw_text.startswith("---"):
            meta = SkillMetadata(id=file_path.stem, description="")
            return cls(metadata=meta, content=raw_text)
            
        parts = raw_text.split("---", 2)
        if len(parts) < 3:
            meta = SkillMetadata(id=file_path.stem, description="")
            return cls(metadata=meta, content=raw_text)
            
        yaml_content = parts[1]
        body_content = parts[2].strip()
        
        try:
            metadata_dict = yaml.safe_load(yaml_content)
            # Ensure required fields
            if "id" not in metadata_dict:
                metadata_dict["id"] = file_path.stem
            if "description" not in metadata_dict:
                metadata_dict["description"] = ""
            metadata = SkillMetadata(**metadata_dict)
        except Exception:
            metadata = SkillMetadata(id=file_path.stem, description="")
            
        return cls(metadata=metadata, content=body_content)

class SkillLoader:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.project_skills_dir = project_root / ".simp" / "skills"
        self.global_skills_dir = Path.home() / ".simpcode" / "skills"

    def load_all_skills(self) -> List[Skill]:
        skills = []
        
        # Load global skills
        if self.global_skills_dir.exists():
            for file in self.global_skills_dir.glob("*.md"):
                skills.append(Skill.from_file(file))
                
        # Load project skills (can shadow global skills)
        if self.project_skills_dir.exists():
            for file in self.project_skills_dir.glob("*.md"):
                # Handle overriding (remove global if same id)
                stem = file.stem
                skills = [s for s in skills if s.metadata.id != stem]
                skills.append(Skill.from_file(file))
                
        return skills

class SkillSelectorResponse(BaseModel):
    selected_skill_ids: List[str]

class SkillSelector:
    """
    SimpCode Skill Selector: Dynamically selects applicable reasoning behaviors (skills)
    based on the current task and project context.
    """
    def __init__(self, llm_client):
        self.llm = llm_client

    def select(self, task: str, available_skills: List[Skill]) -> List[Skill]:
        if not available_skills:
            return []
            
        # Give LLM a catalog of skills and their descriptions
        catalog = "\n".join([f"- ID: {s.metadata.id}\n  Description: {s.metadata.description}" for s in available_skills if s.metadata.description])
        
        if not catalog:
            return []

        prompt = f"""USER TASK: {task}
        
AVAILABLE SKILLS:
{catalog}

Based on the task description, select the IDs of any skills that provide specialized reasoning, domain knowledge, or workflows required to complete this task successfully.
Return ONLY an empty list if no skills are relevant.
"""
        from simpcode.core.prompts import registry
        # We can use a lightweight evaluation prompt
        system_instruction = registry.load("research_assistant") # Or create a dedicated one if we had to
        
        try:
            response = self.llm.structured_output(prompt, SkillSelectorResponse, system_instruction)
            selected = [s for s in available_skills if s.metadata.id in response.selected_skill_ids]
            return selected
        except Exception as e:
            print(f"  [SkillSelector] Warning: Failed to select skills automatically - {e}")
            return []
