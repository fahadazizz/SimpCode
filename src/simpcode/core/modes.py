from pathlib import Path
from typing import List
from simpcode.wiki.engine import WikiEngine
from simpcode.wiki.navigator import WikiNavigator
from simpcode.harness.budgeter import ContextBudgeter, ContextItem
from simpcode.core.llm import LLMClient

class ScanScene:
    def __init__(self, root: Path, llm: LLMClient):
        self.root = root
        self.wiki = WikiEngine(root)
        self.navigator = WikiNavigator(llm)
        self.budgeter = ContextBudgeter()

    def run(self, task: str) -> str:
        # 1. Load mandatory context
        mandatory = []
        for name in ["SIMP.md", "AGENT.md"]:
            p = self.root / name
            if p.exists():
                mandatory.append(ContextItem(id=name, content=p.read_text(), priority=0))
        
        # 2. Load Index
        index_path = self.root / ".simp" / "wiki" / "index.md"
        index_content = index_path.read_text() if index_path.exists() else "# No index found"
        mandatory.append(ContextItem(id="index.md", content=index_content, priority=1))
        
        # 3. Navigate Wiki
        decision = self.navigator.navigate(task, index_content)
        
        # 4. Load semantic pages
        semantic = []
        for page_id in decision.pages_to_load:
            page_path = self.root / ".simp" / "wiki" / f"{page_id}.md"
            if page_path.exists():
                # Check freshness
                # (In a real system, we'd regenerate if stale here)
                semantic.append(ContextItem(id=page_id, content=page_path.read_text(), priority=2))
        
        # 5. Assemble context
        context = self.budgeter.assemble(mandatory, semantic, [])
        return context
