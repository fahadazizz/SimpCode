from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
from simpcode.wiki.models import WikiPage, WikiPageMetadata, SourceReference
import time

class IndexEntry(BaseModel):
    name: str
    type: str  # module, decision, hotspot
    path: str
    description: Optional[str] = None

class IndexManager:
    """
    SimpCode Cartographer: Manages the Project Index with strict context budget discipline.
    Implements prioritized, line-aware pruning to prevent unparseable truncation.
    """
    def __init__(self, wiki_dir: Path, token_budget: int = 1500):
        self.wiki_dir = wiki_dir
        self.token_budget = token_budget
        self.index_path = wiki_dir / "index.md"
        # Token estimation: tiktoken would be better, but character count with buffer is safer than naive math
        self.char_budget = token_budget * 3 

    def update_index(self, modules: List[IndexEntry], decisions: List[IndexEntry], hotspots: List[str]):
        """
        Synthesizes index.md. 
        Trimming order: Hotspots -> Decisions -> Modules.
        """
        # 1. Build sections independently
        module_lines = ["## Modules"] + [f"- [[{m.path}|{m.name}]]: {m.description or ''}" for m in modules]
        decision_lines = ["\n## Decisions"] + [f"- [[decisions/{d}|{d}]]" for d in decisions]
        hotspot_lines = ["\n## Hotspots"] + [f"- {h}" for h in hotspots]
        
        header = "# Project Index\n\nThis is the high-level map of the codebase. Navigation should start here.\n\n"
        
        # 2. Assemble with priority-based pruning
        def assemble_content(h_list, d_list, m_list):
            return header + "\n".join(m_list) + "\n".join(d_list) + "\n".join(h_list)

        # Trimming loop
        while len(assemble_content(hotspot_lines, decision_lines, module_lines)) > self.char_budget:
            if len(hotspot_lines) > 1:
                hotspot_lines.pop() # Remove oldest hotspots first
            elif len(decision_lines) > 1:
                decision_lines.pop()
            elif len(module_lines) > 1:
                module_lines.pop()
            else:
                break # Cannot trim further without losing sections entirely

        final_content = assemble_content(hotspot_lines, decision_lines, module_lines)
        
        metadata = WikiPageMetadata(
            id="index",
            type="structural",
            last_updated=time.time(),
            title="Project Index"
        )
        page = WikiPage(metadata=metadata, content=final_content)
        page.to_file(self.index_path)
