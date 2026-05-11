import os
import subprocess
import time
from pathlib import Path
from typing import List, Optional, Dict
from simpcode.utils.hashes import calculate_file_hash
from simpcode.wiki.engine import WikiEngine
from simpcode.wiki.models import WikiPage
from simpcode.utils.paths import PathManager
from simpcode.core.exclusions import ExclusionFilter

class ToolHarness:
    """
    Execution Harness: Enforces high-integrity filesystem and shell operations.
    Physically prevents any action outside the approved plan scope.
    """
    def __init__(self, root: Path, allowed_files: List[str]):
        self.root = root
        self.path_manager = PathManager()
        self.wiki = WikiEngine(root)
        self.exclusion_filter = ExclusionFilter(root)
        
        # Normalize and resolve all allowed files at startup for deterministic checks
        self.allowed_paths = set()
        for f in allowed_files:
            # We normalize the relative path against root to get an absolute target
            abs_path = (self.root / f).resolve()
            self.allowed_paths.add(str(abs_path))

    def _check_scope(self, file_path: str):
        """
        Structural safety gate: Validates path normalization, plan scope, and exclusions.
        """
        if self.exclusion_filter.is_excluded(file_path):
            raise PermissionError(f"Security Violation: '{file_path}' matches a protected exclusion pattern.")

        full_path = (self.root / file_path).resolve()
        
        # Check against allowed list
        is_allowed = False
        for allowed in self.allowed_paths:
            allowed_path = Path(allowed)
            try:
                if full_path == allowed_path or full_path.is_relative_to(allowed_path):
                    is_allowed = True
                    break
            except ValueError:
                continue
                
        if not is_allowed:
            raise PermissionError(f"Plan Violation: '{file_path}' is not in the approved scope. Operation blocked.")

    def read_file(self, file_path: str) -> str:
        try:
            if self.exclusion_filter.is_excluded(file_path):
                return f"Security Violation: Reading '{file_path}' is structurally blocked by ExclusionFilter."

            full_path = self.path_manager.normalize_path(self.root, file_path)
            if not full_path.exists():
                return f"Error: File '{file_path}' does not exist."
            return full_path.read_text()
        except PermissionError as e:
            return f"Security Violation: {str(e)}"

    def write_file(self, file_path: str, content: str):
        """
        High-integrity write: Enforces scope, creates directories, and updates Wiki.
        """
        self._check_scope(file_path)
        
        full_path = self.root / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        full_path.write_text(content)
        
        # Immediate Semantic Consistency: update knowledge base before next tool call
        self._update_wiki_integrity(file_path)

    def _update_wiki_integrity(self, file_path: str):
        """
        Ensures the Wiki layer is updated IMMEDIATELY after a file write.
        Mark page as STALE (by invalidating hash) to force semantic LLM rewrite on next access.
        """
        pages = self.wiki.get_all_pages()
        
        for page in pages:
            was_staled = False
            for source in page.metadata.sources:
                if source.file_path == file_path:
                    # Invalidate hash instead of blankly updating it
                    source.hash = "NULL_STALE"
                    was_staled = True
            
            if was_staled:
                self.wiki.save_page(page)

    def patch_file(self, file_path: str, old_string: str, new_string: str) -> str:
        """
        Precise patch operation: Preserves file integrity by only changing specified string.
        """
        self._check_scope(file_path)
        
        full_path = self.root / file_path
        if not full_path.exists():
            return f"Error: Cannot patch non-existent file '{file_path}'"
            
        content = full_path.read_text()
        if old_string not in content:
            return "Error: Exact `old_string` not found in file."
            
        new_content = content.replace(old_string, new_string, 1)
        full_path.write_text(new_content)
        
        self._update_wiki_integrity(file_path)
        return "File patched. You MUST run verification next."

    def run_shell(self, command: str) -> str:
        """
        Restricted Shell: Enforces allowlist and project boundaries.
        """
        import re
        import shlex
        
        if re.search(r'[|;&$<>]', command):
            return "Security Error: Shell metacharacters are blocked by the harness."

        base_cmd = command.split()[0]
        # Professional-grade allowlist
        allowlist = ["pytest", "flake8", "ls", "mkdir", "npm", "python", "pip", "git"]
        
        if base_cmd not in allowlist:
            return f"Security Error: Command '{base_cmd}' is not authorized by the harness."
            
        try:
            args = shlex.split(command)
            result = subprocess.run(
                args, 
                shell=False, 
                capture_output=True, 
                text=True, 
                cwd=self.root,
                timeout=120 
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            
            if result.returncode != 0:
                return f"EXECUTION FAILURE (Code {result.returncode}):\n{output}"
            
            return output
        except subprocess.TimeoutExpired:
            return "Error: Command timed out."
        except Exception as e:
            return f"System Error: {str(e)}"
