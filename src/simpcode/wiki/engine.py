import os
from pathlib import Path
from typing import List, Tuple
from simpcode.wiki.models import WikiPage, SourceReference
from simpcode.utils.hashes import calculate_file_hash, calculate_range_hash
from simpcode.core.paths import get_wiki_dir

class WikiEngine:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.wiki_dir = get_wiki_dir()

    def get_all_pages(self) -> List[WikiPage]:
        pages = []
        for file in self.wiki_dir.rglob("*.md"):
            try:
                pages.append(WikiPage.from_file(file))
            except Exception as e:
                # Log error and continue
                print(f"Error loading wiki page {file}: {e}")
        return pages

    def check_staleness(self, page: WikiPage) -> List[Tuple[SourceReference, str]]:
        """
        Returns a list of (SourceReference, current_hash) for sources that are stale.
        """
        stale_sources = []
        for source in page.metadata.sources:
            full_path = self.project_root / source.file_path
            if not full_path.exists():
                stale_sources.append((source, "MISSING"))
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
