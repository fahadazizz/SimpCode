from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel
import time
from simpcode.wiki.models import WikiPage, WikiPageMetadata
from simpcode.wiki.engine import WikiEngine
from simpcode.core.llm import LLMClient
from simpcode.core.prompts import registry

class EvolutionProposals(BaseModel):
    new_patterns: List[str]
    new_risks: List[str]
    new_invariants: List[str]
    change_log_entry: str # Comprehensive semantic summary

class GetBetter:
    """
    SimpCode Knowledge Optimizer: Responsible for reflective learning and Wiki evolution.
    Synthesizes execution traces into persistent architectural knowledge.
    """
    def __init__(self, root: Path, llm: LLMClient):
        self.root = root
        self.llm = llm
        self.wiki = WikiEngine(root)

    def run(self, task: str, execution_trace: str, files_modified: List[str] = None, rationale: str = None):
        system_instruction = registry.load("staff_researcher")
        prompt = registry.load("staff_researcher_learning", include_base=False).format(
            task=task,
            execution_trace=execution_trace,
        )

        proposals = self.llm.structured_output(prompt, EvolutionProposals, system_instruction)
        
        # 1. Update changes.md through the high-integrity WikiEngine
        self.wiki.append_change_log(
            task_description=task,
            files_modified=files_modified or [],
            rationale=rationale or proposals.change_log_entry
        )
        
        # 2. Surface cognitive proposals for human validation
        return proposals

    def append_proposals(self, proposals: EvolutionProposals):
        """Append accepted proposals to respective cognitive wiki layers."""
        self._append_to_cognitive_layer("patterns.md", "Patterns", proposals.new_patterns)
        self._append_to_cognitive_layer("risks.md", "Risks", proposals.new_risks)
        self._append_to_cognitive_layer("invariants.md", "Invariants", proposals.new_invariants)

    def _append_to_cognitive_layer(self, filename: str, title: str, items: List[str]):
        if not items:
            return
            
        page = self.wiki.get_page(filename.replace(".md", ""))
        if not page:
            meta = WikiPageMetadata(id=filename.replace(".md", ""), type="cognitive", last_updated=time.time())
            current_content = f"# {title}\n\nProject {title.lower()}.\n"
            page = WikiPage(metadata=meta, content=current_content)
        else:
            current_content = page.content
            
        # Use LLM to smartly merge and dedup
        from pydantic import BaseModel
        class MergedContent(BaseModel):
            content: str

        prompt = registry.load("wiki_cognitive_merge", include_base=False).format(
            title=title,
            current_content=current_content,
            items=items,
        )
        
        try:
            result = self.llm.structured_output(prompt, MergedContent, "You are a technical document writer preserving project wisdom.")
            new_content = result.content
        except Exception:
            # Fallback if LLM fails
            new_content = current_content + "\n### Added new items\n" + "\n".join(f"- {i}" for i in items)
            
        page.content = new_content
        page.metadata.last_updated = time.time()
        self.wiki.save_page(page)

