import os
from pathlib import Path
from typing import Optional

class PathManager:
    """
    Manages all path resolutions and safety checks for SimpCode.
    Ensures that all operations are relative to the project root and
    handles global vs local storage fallbacks.
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
    def get_global_dir() -> Path:
        """Returns the global ~/.simpcode directory."""
        return Path.home() / ".simpcode"

    @staticmethod
    def get_local_dir(root: Path) -> Path:
        """Returns the project-local .simp directory."""
        return root / ".simp"

    @staticmethod
    def resolve_writable_path(root: Path, filename: str) -> Optional[Path]:
        """
        Resolves a writable path for a given filename, trying global then local.
        Returns None if neither are writable.
        """
        # Try global first
        global_path = PathManager.get_global_dir() / filename
        try:
            global_path.parent.mkdir(parents=True, exist_ok=True)
            # Test writability by touching if not exists
            if not global_path.exists():
                global_path.touch()
            return global_path
        except (PermissionError, OSError):
            pass

        # Try local fallback
        local_path = PathManager.get_local_dir(root) / filename
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            if not local_path.exists():
                local_path.touch()
            return local_path
        except (PermissionError, OSError):
            pass

        return None

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
