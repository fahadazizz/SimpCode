import json
import os
import time
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from simpcode.wiki.models import WikiPage, SourceReference
from simpcode.utils.hashes import calculate_file_hash, calculate_range_hash

class WikiEngine:
    """
    SimpCode Wiki Engine: Orchestrates semantic persistence and self-healing.
    Maintains the dual-layer Markdown graph and source-to-page registry.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.wiki_dir = self.project_root / ".simp" / "wiki"
        self.registry_path = self.wiki_dir / "registry.json"
        self.wiki_dir.mkdir(parents=True, exist_ok=True)

    def _load_registry(self) -> Dict[str, List[str]]:
        if not self.registry_path.exists():
            return {}
        try:
            return json.loads(self.registry_path.read_text())
        except Exception:
            return {}

    def _save_registry(self, registry: Dict[str, List[str]]):
        self.registry_path.write_text(json.dumps(registry, indent=2))

    def get_pages_for_file(self, file_path: str) -> List[str]:
        """Returns IDs of Wiki pages that track the given file (O(1))."""
        registry = self._load_registry()
        return registry.get(file_path, [])

    def get_all_pages(self) -> List[WikiPage]:
        """Discovers all Wiki pages recursively."""
        pages = []
        for file in self.wiki_dir.rglob("*.md"):
            try:
                pages.append(WikiPage.from_file(file))
            except Exception as e:
                print(f"[Wiki] Warning: Could not parse {file.name}: {e}")
        return pages

    def get_page(self, page_id: str) -> Optional[WikiPage]:
        """Retrieves a specific Wiki page by ID."""
        path = self.wiki_dir / f"{page_id}.md"
        if not path.exists():
            return None
        try:
            return WikiPage.from_file(path)
        except Exception:
            return None

    def save_page(self, page: WikiPage):
        """Persists a Wiki page and updates the source registry."""
        path = self.wiki_dir / f"{page.metadata.id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        page.to_file(path)
        
        # Update Registry
        registry = self._load_registry()
        page_id = page.metadata.id
        
        # Remove old entries for this page
        for file_path in list(registry.keys()):
            if page_id in registry[file_path]:
                registry[file_path].remove(page_id)
                if not registry[file_path]:
                    del registry[file_path]
        
        # Add new entries
        for source in page.metadata.sources:
            if source.file_path not in registry:
                registry[source.file_path] = []
            if page_id not in registry[source.file_path]:
                registry[source.file_path].append(page_id)
        
        self._save_registry(registry)

    def sync_hashes(self, page: WikiPage):
        """Updates metadata hashes to match the current on-disk state (High-Integrity)."""
        modified = False
        for source in page.metadata.sources:
            full_path = self.project_root / source.file_path
            if not full_path.exists():
                continue
            
            if source.start_line and source.end_line:
                current_hash = calculate_range_hash(str(full_path), source.start_line, source.end_line)
            else:
                current_hash = calculate_file_hash(str(full_path))
                
            if current_hash != source.hash:
                source.hash = current_hash
                modified = True
        
        if modified:
            page.metadata.last_updated = time.time()
            self.save_page(page)

    def check_staleness(self, page: WikiPage) -> List[Tuple[SourceReference, str]]:
        """Compares recorded hashes against ground-truth files."""
        stale_sources = []
        for source in page.metadata.sources:
            full_path = self.project_root / source.file_path
            if not full_path.exists():
                stale_sources.append((source, "DELETED"))
                continue
            
            if source.start_line and source.end_line:
                current_hash = calculate_range_hash(str(full_path), source.start_line, source.end_line)
            else:
                current_hash = calculate_file_hash(str(full_path))
                
            if current_hash != source.hash:
                stale_sources.append((source, current_hash))
        
        return stale_sources

    def is_page_stale(self, page: WikiPage) -> bool:
        return len(self.check_staleness(page)) > 0

    def append_change_log(self, task_description: str, files_modified: List[str], rationale: str):
        """Appends an entry to the append-only changes.md semantic log (SDD 10.2)."""
        import datetime
        from simpcode.wiki.models import WikiPageMetadata
        
        page = self.get_page("changes")
        if not page:
            meta = WikiPageMetadata(
                id="changes",
                type="change",
                last_updated=time.time(),
                title="Semantic Change Log"
            )
            page = WikiPage(metadata=meta, content="# Semantic Change Log\n\nAppend-only record of system evolution.\n")
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n## {timestamp}\n"
        entry += f"**Task**: {task_description}\n"
        entry += f"**Rationale**: {rationale}\n"
        if files_modified:
            entry += "**Files Modified**:\n"
            for f in files_modified:
                entry += f"- `{f}`\n"
        
        content_parts = page.content.split("\n## ")
        if len(content_parts) > 50:
            page.content = content_parts[0] + "\n## " + "\n## ".join(content_parts[-49:]) + entry
        else:
            page.content += entry
            
        page.metadata.last_updated = time.time()
        self.save_page(page)

