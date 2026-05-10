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

class IndexPage(WikiPage):
    # Specialized WikiPage for index.md
    pass

class IndexManager:
    def __init__(self, wiki_dir: Path, token_budget: int = 1000):
        self.wiki_dir = wiki_dir
        self.token_budget = token_budget
        self.index_path = wiki_dir / "index.md"

    def _estimate_tokens(self, text: str) -> int:
        # Rough estimation: 1 token ~= 4 characters for English text
        return len(text) // 4

    def update_index(self, modules: List[IndexEntry], decisions: List[IndexEntry], hotspots: List[IndexEntry]):
        content = "# Project Index\n\n"
        
        content += "## Modules\n"
        for m in modules:
            content += f"- [[{m.path}|{m.name}]]: {m.description or ''}\n"
        
        content += "\n## Decisions\n"
        for d in decisions:
            content += f"- [[{d.path}|{d.name}]]\n"
            
        content += "\n## Hotspots\n"
        for h in hotspots:
            content += f"- {h.path}\n"
            
        # Check budget
        while self._estimate_tokens(content) > self.token_budget:
            # Simple trimming logic: remove hotspots first, then decisions
            if "## Hotspots" in content and content.split("## Hotspots")[1].strip():
                lines = content.split("\n")
                # Remove last line of hotspots
                content = "\n".join(lines[:-1])
            elif "## Decisions" in content and content.split("## Decisions")[1].strip():
                # Trimming decisions is more complex, but let's just truncate for now
                content = content[:int(len(content)*0.9)]
            else:
                # Truncate content if still over budget
                content = content[:int(len(content)*0.9)]
                
        metadata = WikiPageMetadata(
            id="index",
            type="structural",
            last_updated=time.time(),
            title="Project Index"
        )
        page = WikiPage(metadata=metadata, content=content)
        page.to_file(self.index_path)
