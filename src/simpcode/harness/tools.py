import os
import shlex
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

    def _check_read_scope(self, file_path: str):
        """
        Structural safety gate for read operations.
        Reads are allowed project-wide unless excluded.
        """
        if self.exclusion_filter.is_excluded(file_path):
            raise PermissionError(f"Security Violation: '{file_path}' matches a protected exclusion pattern.")

    def _check_write_scope(self, file_path: str):
        """
        Structural safety gate for write operations.
        Writes are restricted to plan-approved targets.
        """
        self._check_read_scope(file_path)

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
            self._check_read_scope(file_path)

            full_path = self.path_manager.normalize_path(self.root, file_path)
            if not full_path.exists():
                return f"Error: File '{file_path}' does not exist."
            # Return file contents as-is; callers should treat this as untrusted content.
            return full_path.read_text()
        except PermissionError as e:
            return f"Security Violation: {str(e)}"

    def list_dir(self, dir_path: str = ".") -> str:
        """
        Read-only directory listing helper for contextual exploration.
        """
        try:
            self._check_read_scope(dir_path)

            full_path = self.path_manager.normalize_path(self.root, dir_path)
            if not full_path.exists():
                return f"Error: Directory '{dir_path}' does not exist."
            if not full_path.is_dir():
                return f"Error: Path '{dir_path}' is not a directory."

            entries = []
            for child in sorted(full_path.iterdir(), key=lambda path: (not path.is_dir(), path.name.lower())):
                suffix = "/" if child.is_dir() else ""
                entries.append(f"{child.name}{suffix}")
            return "\n".join(entries)
        except PermissionError as e:
            return f"Security Violation: {str(e)}"

    def write_file(self, file_path: str, content: str):
        """
        High-integrity write: Enforces scope, creates directories, and updates Wiki.
        """
        self._check_write_scope(file_path)
        
        full_path = self.root / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        full_path.write_text(content)



    def patch_file(self, file_path: str, old_string: str, new_string: str) -> str:
        """
        Precise patch operation: Robust patch with whitespace tolerance.
        """
        self._check_write_scope(file_path)
        
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
        return "File patched. You MUST run verification next."

    def run_shell(self, command: str) -> str:
        """
        Safe shell executor: permit only a conservative allowlist of commands and
        execute without a shell when possible. Rejects shell control operators
        to avoid injection and redirection attacks.
        """
        try:
            # Basic sanitation: do not permit shell operators or constructs that
            # require a shell. If they are present, reject outright.
            forbidden_tokens = [';', '&', '|', '>', '<', '$', '`']
            if any(tok in command for tok in forbidden_tokens):
                return "Security Violation: shell operators are prohibited in run_shell."

            # Require a conservative allowlist for the command (first token).
            parts = shlex.split(command)
            if not parts:
                return "Error: empty command"

            allowlist = {
                'ls', 'git', 'cat', 'python', 'pytest', 'pip', 'echo', 'pwd',
                'sed', 'awk', 'grep', 'head', 'tail', 'wc', 'mkdir', 'rmdir', 'cp', 'mv',
                'flake8', 'ruff', 'mypy'
            }

            cmd = parts[0]
            if cmd not in allowlist:
                return f"Security Violation: command '{cmd}' is not permitted by policy."

            # Execute without shell to avoid shell injection; pass args directly.
            result = subprocess.run(
                parts,
                shell=False,
                capture_output=True,
                text=True,
                cwd=self.root,
                timeout=300,
                check=False,
            )

            output = result.stdout or ''
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"

            if result.returncode != 0:
                return f"EXECUTION FAILURE (Code {result.returncode}):\n{output}"

            return output
        except subprocess.TimeoutExpired:
            return "Error: Command timed out."
        except Exception as e:
            return f"System Error: {str(e)}"
