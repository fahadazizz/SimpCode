import os
import time
from pathlib import Path
from typing import List, Tuple, Optional
from simpcode.wiki.models import WikiPage, SourceReference
from simpcode.utils.hashes import calculate_file_hash, calculate_range_hash
from simpcode.core.paths import get_wiki_dir

class WikiEngine:
    """
    SimpCode Wiki Engine: Orchestrates semantic persistence and self-healing.
    Maintains the dual-layer Markdown graph.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.wiki_dir = get_wiki_dir()

    def get_all_pages(self) -> List[WikiPage]:
        """
        Discovers all Wiki pages recursively.
        """
        pages = []
        for file in self.wiki_dir.rglob("*.md"):
            try:
                pages.append(WikiPage.from_file(file))
            except Exception as e:
                # Log corruption but don't crash
                print(f"[Wiki] Warning: Could not parse {file.name}: {e}")
        return pages

    def get_page(self, page_id: str) -> Optional[WikiPage]:
        """
        Retrieves a specific Wiki page by ID.
        """
        # Resolve ID to path (e.g., 'modules/core' -> '.simp/wiki/modules/core.md')
        path = self.wiki_dir / f"{page_id}.md"
        if not path.exists():
            return None
        try:
            return WikiPage.from_file(path)
        except Exception:
            return None

    def save_page(self, page: WikiPage):
        """
        Persists a Wiki page to disk.
        """
        path = self.wiki_dir / f"{page.metadata.id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        page.to_file(path)

    def check_staleness(self, page: WikiPage) -> List[Tuple[SourceReference, str]]:
        """
        High-integrity verification: Compares recorded hashes against ground-truth files.
        Returns list of (stale_reference, current_actual_hash).
        """
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
