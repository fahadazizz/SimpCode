from pathlib import Path
import os
from typing import Optional

class PromptLoader:
    """
    SimpCode Prompt Registry: Manages the externalized reasoning layer.
    Loads highly-optimized system prompts from the prompts/ directory.
    Supports composition of Base Principles with Role-Specific instructions.
    """
    def __init__(self):
        # Resolve the prompts directory relative to this file
        self.prompts_dir = Path(__file__).parent
        
    def load(self, prompt_name: str, include_base: bool = True) -> str:
        """
        Loads a prompt by name and optionally prepends the Base Principles.
        """
        if not prompt_name.endswith(".md"):
            prompt_name += ".md"
            
        file_path = self.prompts_dir / prompt_name
        if not file_path.exists():
            raise FileNotFoundError(f"System Prompt Artifact '{prompt_name}' not found at {file_path}")
            
        content = file_path.read_text().strip()
        
        if include_base and prompt_name != "base_principles.md":
            base = self.load("base_principles.md", include_base=False)
            return f"{base}\n\n---\n\n{content}"
            
        return content

# Singleton instance for easy access
registry = PromptLoader()
