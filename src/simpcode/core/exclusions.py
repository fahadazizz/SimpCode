from pathlib import Path
from typing import List
import os

class ExclusionFilter:
    """
    SimpCode Exclusion Filter: Ensures protected files (secrets, environments)
    are structurally excluded from all interactions.
    """
    def __init__(self, root: Path):
        self.root = root
        self.exclusion_patterns = set([
            ".env", ".env.*", "secrets.json", "*.key", "*.pem", 
            "id_rsa", ".git/*", ".simp/*", ".simpcode/*", "node_modules/*", "__pycache__/*"
        ])
        self._load_gitignore()

    def _load_gitignore(self):
        gitignore_path = self.root / ".gitignore"
        if gitignore_path.exists():
            for line in gitignore_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    self.exclusion_patterns.add(line)

    def is_excluded(self, path: str) -> bool:
        """
        Check if a given path matches any exclusion patterns.
        """
        import fnmatch
        full_path = self.root / path
        rel_path = str(full_path.relative_to(self.root))
        
        for pattern in self.exclusion_patterns:
            # Basic glob matching
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(full_path.name, pattern):
                return True
            
            # Directory matching
            if pattern.endswith('/') and rel_path.startswith(pattern.strip('/')):
                return True
            if not pattern.endswith('/') and any(p == pattern for p in Path(rel_path).parts):
                return True
                
        return False
