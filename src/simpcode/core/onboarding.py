from pathlib import Path

from simpcode.core.analyzer import ProjectMetadata
from simpcode.core.generator import SynthesizedDocs
from simpcode.wiki.models import WikiPage, WikiPageMetadata


def needs_onboarding(root: Path) -> bool:
    """Check if the project requires initialization."""
    simp_md = root / "SIMP.md"
    index_md = root / ".simp" / "wiki" / "index.md"
    # If either core manifest or the semantic index is missing, we need onboarding
    return not simp_md.exists() or not index_md.exists()


def ensure_onboarding_artifacts(
    root: Path,
    docs: SynthesizedDocs,
    metadata: ProjectMetadata,
    overwrite_spec: bool = False,
) -> None:
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

    wiki_dir = root / ".simp" / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)

    index_path = wiki_dir / "index.md"
    if not index_path.exists():
        import time
        meta = WikiPageMetadata(id="index", type="structural", last_updated=time.time())
        content = "# Project Wiki\n\n- [patterns](patterns.md)\n- [risks](risks.md)\n- [invariants](invariants.md)"
        WikiPage(metadata=meta, content=content).to_file(index_path)
