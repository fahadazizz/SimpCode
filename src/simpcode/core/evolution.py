from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel
import time
from simpcode.wiki.models import WikiPage, WikiPageMetadata
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
        self.wiki_dir = self.root / ".simp" / "wiki"
        self.wiki_dir.mkdir(parents=True, exist_ok=True)

    def run(self, task: str, execution_trace: str):
        system_instruction = registry.load("staff_researcher")
        prompt = registry.load("staff_researcher_learning", include_base=False).format(
            task=task,
            execution_trace=execution_trace,
        )

        proposals = self.llm.structured_output(prompt, EvolutionProposals, system_instruction)
        
        # 1. Update changes.md (Structural update is automatic)
        self._append_to_changes(proposals.change_log_entry)
        
        # 2. Surface cognitive proposals for human validation
        return proposals

    def _append_to_changes(self, entry: str):
        path = self.wiki_dir / "changes.md"
        header = f"\n### [{time.strftime('%Y-%m-%d %H:%M:%S')}] Evolution\n"
        
        if not path.exists():
            meta = WikiPageMetadata(id="changes", type="structural", last_updated=time.time())
            WikiPage(metadata=meta, content="# Change Log\n\nSemantic history of system evolution.").to_file(path)
            
        with open(path, "a") as f:
            f.write(header + entry + "\n")

    def append_proposals(self, proposals: EvolutionProposals):
        """Append accepted proposals to respective cognitive wiki layers."""
        self._append_to_cognitive_layer("patterns.md", "Patterns", proposals.new_patterns)
        self._append_to_cognitive_layer("risks.md", "Risks", proposals.new_risks)
        self._append_to_cognitive_layer("invariants.md", "Invariants", proposals.new_invariants)

    def _append_to_cognitive_layer(self, filename: str, title: str, items: List[str]):
        if not items:
            return
            
        path = self.wiki_dir / filename
        meta = None
        if not path.exists():
            from simpcode.wiki.models import WikiPageMetadata, WikiPage
            import time
            meta = WikiPageMetadata(id=filename.split(".")[0], type="cognitive", last_updated=time.time())
            current_content = f"# {title}\n\nProject {title.lower()}.\n"
        else:
            from simpcode.wiki.models import WikiPage
            page = WikiPage.from_file(path)
            meta = page.metadata
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
            
        from simpcode.wiki.models import WikiPage
        import time
        meta.last_updated = time.time()
        WikiPage(metadata=meta, content=new_content).to_file(path)
