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
        raw_file_tree = []
        manifests = {}
        entry_point_samples = {}
        
        # 1. Map File Tree
        for p in self.root.rglob("*"):
            rel_path = str(p.relative_to(self.root))
            if self.exclusion_filter.is_excluded(rel_path):
                continue
            if p.is_file():
                raw_file_tree.append(rel_path)
                
                # 2. Extract Manifests
                manifest_names = {"pyproject.toml", "package.json", "requirements.txt", "Makefile", "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "Gemfile"}
                manifest_exts = {".csproj", ".fsproj", ".sln", ".gemspec", ".gradle"}
                
                if p.name in manifest_names or p.suffix in manifest_exts:
                    try:
                        manifests[rel_path] = p.read_text()[:5000] # Limit size
                    except Exception:
                        pass
                
                # 3. Extract Entry Point Samples (Common patterns)
                entry_stems = {"main", "app", "index", "server", "manage", "run", "cli", "bootstrap", "setup"}
                valid_exts = {".py", ".js", ".ts", ".go", ".rs", ".rb", ".java", ".cpp", ".cs", ".php", ".sh"}
                
                if p.stem.lower() in entry_stems and p.suffix.lower() in valid_exts:
                    try:
                        entry_point_samples[rel_path] = p.read_text()[:2000] # Snippet
                    except Exception:
                        pass

        # Hierarchical compression if too large
        if len(raw_file_tree) <= 500:
            file_tree = raw_file_tree
        else:
            file_tree = []
            dir_counts = {}
            for f in raw_file_tree:
                parts = f.split("/")
                if len(parts) > 3:
                    dir_path = "/".join(parts[:3]) + "/*"
                    dir_counts[dir_path] = dir_counts.get(dir_path, 0) + 1
                else:
                    file_tree.append(f)
            
            for d, count in dir_counts.items():
                file_tree.append(f"{d} ({count} files)")
                
            # If still too large, fallback to truncation
            file_tree = file_tree[:2000]

        return ProjectMetadata(
            name=self.root.name,
            root=str(self.root),
            file_tree=file_tree,
            manifests=manifests,
            entry_point_samples=entry_point_samples
        )
