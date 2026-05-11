import os
from pathlib import Path
from typing import Optional

class PathManager:
    """
    Manages all path resolutions and safety checks for SimpCode.
    Ensures that all operations are relative to the project root.
    """
    
    @staticmethod
    def find_project_root(current_dir: Optional[Path] = None) -> Path:
        """
        Recursively looks for a project root marker (e.g., .simp, .git, pyproject.toml).
        """
        if current_dir is None:
            current_dir = Path.cwd()
            
        markers = [".simp", ".git", "pyproject.toml", "package.json"]
        
        # Check current directory
        for marker in markers:
            if (current_dir / marker).exists():
                return current_dir
        
        # Check parent
        if current_dir.parent == current_dir:
            # Reached the actual filesystem root
            return Path.cwd() # Fallback to CWD if no root found
            
        return PathManager.find_project_root(current_dir.parent)

    @staticmethod
    def normalize_path(root: Path, path_str: str) -> Path:
        """
        Normalizes a path string relative to the root and checks for traversal.
        """
        path = Path(path_str)
        if not path.is_absolute():
            path = root / path
            
        normalized = path.resolve()
        
        # Security: Prevent directory traversal outside of root
        if not str(normalized).startswith(str(root.resolve())):
            raise PermissionError(f"Security Violation: Access to {path_str} is outside project root.")
            
        return normalized

    @staticmethod
    def get_relative_path(root: Path, full_path: Path) -> str:
        """
        Returns the path relative to root as a string.
        """
        return str(full_path.resolve().relative_to(root.resolve()))
