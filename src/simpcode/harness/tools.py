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
        Updates hash to actual file hash so it doesn't drop from context.
        """
        pages = self.wiki.get_all_pages()
        
        for page in pages:
            was_staled = False
            for source in page.metadata.sources:
                if source.file_path == file_path:
                    full_source_path = self.root / source.file_path
                    if full_source_path.exists():
                        from simpcode.utils.hashes import calculate_file_hash
                        if source.start_line and source.end_line:
                            from simpcode.utils.hashes import calculate_range_hash
                            source.hash = calculate_range_hash(str(full_source_path), source.start_line, source.end_line)
                        else:
                            source.hash = calculate_file_hash(str(full_source_path))
                    else:
                        source.hash = "DELETED"
                    was_staled = True
            
            if was_staled:
                self.wiki.save_page(page)

    def patch_file(self, file_path: str, old_string: str, new_string: str) -> str:
        """
        Precise patch operation: Robust patch with whitespace tolerance.
        """
        self._check_scope(file_path)
        
        full_path = self.root / file_path
        if not full_path.exists():
            return f"Error: Cannot patch non-existent file '{file_path}'"
            
        content = full_path.read_text()
        
        if old_string in content:
            new_content = content.replace(old_string, new_string, 1)
        else:
            import re
            def normalize(s):
                return re.sub(r'\s+', '', s)
                
            norm_old = normalize(old_string)
            if not norm_old:
                return "Error: Empty old_string provided."
                
            pattern_str = r'\s*'.join(re.escape(c) for c in norm_old)
            pattern = re.compile(pattern_str)
            
            matches = list(pattern.finditer(content))
            if len(matches) == 1:
                match = matches[0]
                new_content = content[:match.start()] + new_string + content[match.end():]
            elif len(matches) > 1:
                return "Error: Multiple matches found for old_string (whitespace-agnostic). Be more specific."
            else:
                return "Error: Exact `old_string` not found in file, even with varying whitespace."
                
        full_path.write_text(new_content)
        
        self._update_wiki_integrity(file_path)
        return "File patched. You MUST run verification next."

    def run_shell(self, command: str) -> str:
        """
        Advanced Shell: Unrestricted shell for production engineering.
        """
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=self.root,
                timeout=300 
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
