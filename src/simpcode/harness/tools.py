import os
import subprocess
from pathlib import Path
from typing import List, Optional
from simpcode.utils.hashes import calculate_file_hash
from simpcode.wiki.engine import WikiEngine
from simpcode.wiki.models import WikiPage

class ToolHarness:
    def __init__(self, root: Path, allowed_files: List[str]):
        self.root = root
        self.allowed_files = allowed_files # From the approved plan
        self.wiki = WikiEngine(root)

    def _check_scope(self, file_path: str):
        # In a real system, this would be more robust (e.g., path resolution)
        if file_path not in self.allowed_files:
            raise PermissionError(f"Access to {file_path} is out of plan scope.")

    def read_file(self, file_path: str) -> str:
        # No scope check for reads in our spec, but good practice
        full_path = self.root / file_path
        if not full_path.exists():
            return ""
        return full_path.read_text()

    def write_file(self, file_path: str, content: str):
        self._check_scope(file_path)
        full_path = self.root / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read-before-write is implicitly handled by the agent, 
        # but we can log state here if needed.
        
        full_path.write_text(content)
        
        # Inline Wiki Update (Stub for symbol updates, but hash is real)
        # In Phase 5, we ensure hashes are updated.
        self._update_wiki_hashes(file_path)

    def _update_wiki_hashes(self, file_path: str):
        # Find all wiki pages that reference this file
        pages = self.wiki.get_all_pages()
        new_hash = calculate_file_hash(str(self.root / file_path))
        
        for page in pages:
            updated = False
            for source in page.metadata.sources:
                if source.file_path == file_path:
                    source.hash = new_hash
                    updated = True
            
            if updated:
                # Save the updated wiki page back to disk
                page_path = self.wiki.wiki_dir / f"{page.metadata.id}.md"
                page.to_file(page_path)

    def run_shell(self, command: str) -> str:
        # Simple allowlist check
        allowlist = ["pytest", "flake8", "ls", "mkdir", "npm test"]
        base_cmd = command.split()[0]
        if base_cmd not in allowlist:
            raise PermissionError(f"Command '{base_cmd}' is not on the allowlist.")
            
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=self.root)
        if result.returncode != 0:
            return f"ERROR: {result.stderr}"
        return result.stdout
