from pathlib import Path
from typing import List, Optional

from simpcode.core.analyzer import ProjectMetadata
from simpcode.core.generator import SynthesizedDocs
from simpcode.wiki.models import WikiPage, WikiPageMetadata
from simpcode.core.resources import SIMP_TEMPLATE, SPEC_TEMPLATE, WIKI_INDEX_TEMPLATE


def needs_onboarding(root: Path) -> bool:
    """Check if the project requires initialization."""
    simp_md = root / "SIMP.md"
    index_md = root / ".simp" / "wiki" / "index.md"
    # If either core manifest or the semantic index is missing, we need onboarding
    return not simp_md.exists() or not index_md.exists()


def write_skeleton_artifacts(root: Path) -> None:
    """
    Initializes a new project with static templates.
    No LLM synthesis required.
    """
    root.mkdir(parents=True, exist_ok=True)
    
    # 1. Write SIMP.md
    simp_path = root / "SIMP.md"
    if not simp_path.exists():
        simp_path.write_text(SIMP_TEMPLATE)

    # 2. Write SPEC.md
    spec_path = root / "SPEC.md"
    if not spec_path.exists():
        spec_path.write_text(SPEC_TEMPLATE.format(project_name=root.name))

    # 3. Setup Wiki Skeleton
    wiki_dir = root / ".simp" / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)
    for d in ["modules", "symbols", "decisions"]:
        (wiki_dir / d).mkdir(exist_ok=True)

    index_path = wiki_dir / "index.md"
    if not index_path.exists():
        import time
        meta = WikiPageMetadata(id="index", type="structural", last_updated=time.time())
        WikiPage(metadata=meta, content=WIKI_INDEX_TEMPLATE).to_file(index_path)

    # Create empty base nodes for patterns/risks/invariants
    for node in ["patterns", "risks", "invariants"]:
        node_path = wiki_dir / f"{node}.md"
        if not node_path.exists():
            import time
            meta = WikiPageMetadata(id=node, type="cognitive", last_updated=time.time())
            WikiPage(metadata=meta, content=f"# {node.capitalize()}\n\nNo {node} identified yet.\n").to_file(node_path)


def ensure_onboarding_artifacts(
    root: Path,
    docs: Optional[SynthesizedDocs] = None,
    metadata: Optional[ProjectMetadata] = None,
    overwrite_spec: bool = False,
) -> None:
    """
    Ensures core artifacts exist. If docs are provided (Legacy synthesis), 
    it uses them. Otherwise, it defaults to skeleton.
    """
    if docs is None:
        write_skeleton_artifacts(root)
        return

    root.mkdir(parents=True, exist_ok=True)

    simp_path = root / "SIMP.md"
    if not simp_path.exists():
        simp_path.write_text(docs.simp_md.strip() + "\n")

    spec_path = root / "SPEC.md"
    spec_content = docs.spec_md.strip()

    if spec_content:
        spec_path.write_text(spec_content + "\n")
    elif overwrite_spec and spec_path.exists():
        spec_path.unlink()
    elif not spec_path.exists():
        # Even in legacy mode, if no spec generated, write template
        spec_path.write_text(SPEC_TEMPLATE.format(project_name=root.name))

    # Ensure wiki dir structure
    write_skeleton_artifacts(root)
