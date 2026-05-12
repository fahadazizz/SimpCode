from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import time
from simpcode.wiki.models import WikiPage, WikiPageMetadata, SourceReference
from simpcode.core.llm import LLMClient
from simpcode.core.analyzer import ProjectMetadata
from simpcode.wiki.index import IndexManager, IndexEntry
from simpcode.utils.hashes import calculate_file_hash
from simpcode.core.prompts import registry

class BootstrapResult(BaseModel):
    cognitive_pages: Dict[str, str] # filename -> content
    modules: Dict[str, str] # module_name -> purpose_description
    symbol_targets: List[str] # List of critical symbols to index next

class WikiBootstrap:
    """
    SimpCode Knowledge Ingestion: Systematic codebase 'compilation' into the Wiki.
    Builds the structural and cognitive foundations from entry points outward.
    """
    def __init__(self, llm: LLMClient, root: Path):
        self.llm = llm
        self.root = root
        self.wiki_dir = root / ".simp" / "wiki"
        self._ensure_dirs()

    def _ensure_dirs(self):
        self.wiki_dir.mkdir(parents=True, exist_ok=True)
        (self.wiki_dir / "modules").mkdir(exist_ok=True)
        (self.wiki_dir / "symbols").mkdir(exist_ok=True)
        (self.wiki_dir / "decisions").mkdir(exist_ok=True)

    def run(self, metadata: ProjectMetadata):
        system_instruction = registry.load("wiki_librarian")
        prompt = registry.load("wiki_bootstrap", include_base=False).format(
            root=metadata.root,
            file_tree=metadata.file_tree,
            manifests=metadata.manifests,
            entry_point_samples=metadata.entry_point_samples,
        )
        result = self.llm.structured_output(prompt, BootstrapResult, system_instruction)
        
        # 1. Write Cognitive Pages
        for name, content in result.cognitive_pages.items():
            if not name.endswith(".md"): name += ".md"
            meta = WikiPageMetadata(id=name.replace(".md", ""), type="cognitive", last_updated=time.time())
            WikiPage(metadata=meta, content=content).to_file(self.wiki_dir / name)
            
        # 2. Write Module Pages (First Pass)
        module_entries = []
        for mod_name, description in result.modules.items():
            page_id = f"modules/{mod_name}"
            sources = []
            potential_file = self._guess_main_file(mod_name, metadata.file_tree)
            if potential_file:
                sources.append(SourceReference(
                    file_path=potential_file,
                    hash=calculate_file_hash(str(self.root / potential_file))
                ))
                
            meta = WikiPageMetadata(
                id=page_id, 
                type="module", 
                sources=sources,
                last_updated=time.time(),
                title=f"Module: {mod_name}"
            )
            content = f"# {mod_name}\n\n{description}\n\n## Responsibilities\n- (Compiled Pass 1)"
            WikiPage(metadata=meta, content=content).to_file(self.wiki_dir / f"{page_id}.md")
            
            module_entries.append(IndexEntry(
                name=mod_name, 
                type="module", 
                path=page_id, 
                description=description[:200]
            ))
            
        # 3. Initialize Project Index
        idx_manager = IndexManager(self.wiki_dir)
        idx_manager.update_index(module_entries, [], [])

    def _guess_main_file(self, mod_name: str, file_tree: List[str]) -> Optional[str]:
        # Language-agnostic module resolution
        targets = [
            # Python
            f"{mod_name}/__init__.py",
            f"{mod_name}.py",
            f"src/{mod_name}/__init__.py",
            f"src/{mod_name}.py",
            # JS/TS
            f"{mod_name}/index.ts",
            f"{mod_name}/index.js",
            f"{mod_name}.ts",
            f"{mod_name}.js",
            f"src/{mod_name}/index.ts",
            f"src/{mod_name}/index.js",
            # Rust / Go
            f"{mod_name}/main.rs",
            f"{mod_name}/lib.rs",
            f"{mod_name}/main.go",
        ]
        
        for t in targets:
            if t in file_tree:
                return t
                
        # Fallback: fuzzy match
        for file in file_tree:
            if f"{mod_name}" in file:
                return file
                
        return None