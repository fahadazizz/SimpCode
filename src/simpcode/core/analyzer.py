import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from simpcode.utils.paths import PathManager
from simpcode.core.exclusions import ExclusionFilter

class ProjectMetadata(BaseModel):
    name: str
    root: str
    file_tree: List[str]
    manifests: Dict[str, str] # filename -> content
    entry_point_samples: Dict[str, str] # filename -> first 50 lines

class ProjectAnalyzer:
    """
    Collects raw codebase data for LLM synthesis.
    Does NOT attempt to "understand" the project itself.
    """
    def __init__(self, root: Path):
        self.root = root
        self.exclusion_filter = ExclusionFilter(root)

    def collect_metadata(self) -> ProjectMetadata:
        file_tree = []
        manifests = {}
        entry_point_samples = {}
        
        # 1. Map File Tree (shallow for large projects)
        for p in self.root.rglob("*"):
            rel_path = str(p.relative_to(self.root))
            if self.exclusion_filter.is_excluded(rel_path):
                continue
            if p.is_file():
                file_tree.append(rel_path)
                
                # 2. Extract Manifests
                if p.name in ["pyproject.toml", "package.json", "requirements.txt", "Makefile", "go.mod"]:
                    try:
                        manifests[rel_path] = p.read_text()[:5000] # Limit size
                    except Exception:
                        pass
                
                # 3. Extract Entry Point Samples (Common names)
                if p.name in ["main.py", "app.py", "index.ts", "server.js", "main.go"]:
                    try:
                        entry_point_samples[rel_path] = p.read_text()[:2000] # Snippet
                    except Exception:
                        pass

        return ProjectMetadata(
            name=self.root.name,
            root=str(self.root),
            file_tree=file_tree[:500], # Limit tree size for LLM
            manifests=manifests,
            entry_point_samples=entry_point_samples
        )
