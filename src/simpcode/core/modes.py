from pathlib import Path
from typing import List, Set
from simpcode.wiki.engine import WikiEngine
from simpcode.wiki.navigator import WikiNavigator
from simpcode.harness.budgeter import ContextBudgeter, ContextItem
from simpcode.core.llm import LLMClient
from simpcode.wiki.models import WikiPage
from simpcode.core.skills import SkillLoader, SkillSelector
from simpcode.core.prompts import registry
import time
from simpcode.utils.hashes import calculate_file_hash, calculate_range_hash

class ScanScene:
    """
    SimpCode Situational Awareness: Systematically assembles relevant task context.
    Enforces "Wiki-First" and implements multi-pass intentional navigation.
    """
    def __init__(self, root: Path, llm: LLMClient):
        self.root = root
        self.llm = llm
        self.wiki = WikiEngine(root)
        self.navigator = WikiNavigator(llm)
        self.budgeter = ContextBudgeter(model=llm.model_id)
        self.skill_loader = SkillLoader(root)
        self.skill_selector = SkillSelector(llm)

    def run(self, task: str) -> str:
        # 1. Load Ground-Truth Context (Constitutional Identity)
        mandatory = []
        for name in ["SIMP.md", "SPEC.md"]:
            p = self.root / name
            if p.exists():
                mandatory.append(ContextItem(id=name, content=p.read_text(), priority=0))
        
        # 1.1 Load and Verify Mandatory Wiki Nodes (SDD 7.2)
        for page_id in ["index", "invariants"]:
            page = self.wiki.get_page(page_id)
            if not page:
                continue
            
            if self.wiki.is_page_stale(page):
                print(f"  [Scan] Auto-healing ground-truth: {page_id}")
                self._heal_page(page)
            
            mandatory.append(ContextItem(id=f"{page_id}.md", content=page.content, priority=1))
        
        index_page = self.wiki.get_page("index")
        index_content = index_page.content if index_page else "# No index found"
        
        # 1.5 Load Relevant Skills
        available_skills = self.skill_loader.load_all_skills()
        selected_skills = self.skill_selector.select(task, available_skills)
        for skill in selected_skills:
            print(f"  [Scan] Selected Skill: {skill.metadata.id} - {skill.metadata.description}")
            mandatory.append(ContextItem(id=f"SKILL: {skill.metadata.id}", content=skill.content, priority=1))

        # 2. Multi-Pass Strategic Navigation
        loaded_page_ids: Set[str] = {"index", "invariants"}
        semantic_items: List[ContextItem] = []
        targeted_items: List[ContextItem] = []
        
        max_passes = 2 
        for pass_num in range(max_passes):
            decision = self.navigator.navigate(
                f"{task}\n(Currently loaded: {', '.join(loaded_page_ids)})", 
                index_content
            )
            
            new_pages = [p for p in decision.pages_to_load if p not in loaded_page_ids]
            if not new_pages:
                break
                
            for page_id in new_pages:
                page = self.wiki.get_page(page_id)
                if not page:
                    continue
                
                loaded_page_ids.add(page_id)
                
                # Check Freshness per Spec 7.2 & 4.4
                if self.wiki.is_page_stale(page):
                    print(f"  [Scan] Auto-healing stale Wiki page: {page_id}")
                    self._heal_page(page)
                
                semantic_items.append(ContextItem(id=page_id, content=page.content, priority=2))
                # Resolve File:Line pointers (Targeted Tier)
                from simpcode.utils.hashes import read_range
                for source in page.metadata.sources:
                    if source.start_line and source.end_line:
                        try:
                            code = read_range(str(self.root / source.file_path), source.start_line, source.end_line)
                            targeted_items.append(ContextItem(
                                id=f"CODE: {source.file_path} ({source.start_line}-{source.end_line})",
                                content=code,
                                priority=3
                            ))
                        except Exception as e:
                            print(f"  [Scan] Error reading range for {source.file_path}: {e}")

        # 3. Deterministic Assembly (Tiered Budget Enforcement)
        return self.budgeter.assemble(mandatory, semantic_items, targeted_items)

    def _heal_page(self, page: WikiPage):
        """Regenerates a Wiki page to match current source truth."""
        instruction = registry.load("wiki_maintainer")
        code_context = ""
        for source in page.metadata.sources:
            full_path = self.root / source.file_path
            if full_path.exists():
                code_context += f"--- {source.file_path} ---\n{full_path.read_text()[:5000]}\n\n"
        
        if code_context:
            prompt = f"OLD CONTENT:\n{page.content}\n\nCurrent Code:\n{code_context}\n\nUpdate page."
            page.content = self.llm.chat([{"role": "user", "content": prompt}], instruction)
            self.wiki.sync_hashes(page) # High-Integrity Sync
        else:
            print(f"  [Scan] Warning: Source files deleted for {page.metadata.id}. Excluded.")

