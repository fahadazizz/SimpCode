from pathlib import Path
import time

from simpcode.core.analyzer import ProjectMetadata
from simpcode.core.generator import SynthesizedDocs
from simpcode.wiki.models import WikiPage, WikiPageMetadata


def needs_onboarding(root: Path) -> bool:
    simp_md = root / "SIMP.md"
    index_md = root / ".simp" / "wiki" / "index.md"
    return not simp_md.exists() or not index_md.exists()


def ensure_onboarding_artifacts(root: Path, docs: SynthesizedDocs, metadata: ProjectMetadata) -> None:
    root.mkdir(parents=True, exist_ok=True)

    simp_path = root / "SIMP.md"
    simp_content = docs.simp_md.strip() or _fallback_simp_content(metadata)
    if not simp_path.exists() or not simp_path.read_text().strip():
        simp_path.write_text(simp_content + "\n")

    spec_path = root / "SPEC.md"
    spec_content = docs.spec_md.strip()
    if spec_content:
        spec_path.write_text(spec_content + "\n")
    elif spec_path.exists():
        spec_path.unlink()

    index_path = root / ".simp" / "wiki" / "index.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if not index_path.exists():
        fallback_index = WikiPage(
            metadata=WikiPageMetadata(
                id="index",
                type="structural",
                last_updated=time.time(),
                title="Project Index",
            ),
            content=_fallback_index_content(metadata),
        )
        fallback_index.to_file(index_path)


def _fallback_simp_content(metadata: ProjectMetadata) -> str:
    lines = [
        "# SIMP",
        "",
        f"Project: {metadata.name}",
        f"Root: {metadata.root}",
        "",
        "## Overview",
        "- Auto-generated fallback manifest created during onboarding.",
        "- Review and replace with project-specific intelligence after init.",
    ]
    return "\n".join(lines)


def _fallback_index_content(metadata: ProjectMetadata) -> str:
    preview = metadata.file_tree[:80]
    lines = [
        "# Project Index",
        "",
        "Fallback onboarding index created because the semantic index was missing.",
        "",
        "## Files",
    ]
    lines.extend(f"- {item}" for item in preview)
    if len(metadata.file_tree) > len(preview):
        lines.append(f"- ... and {len(metadata.file_tree) - len(preview)} more files")
    return "\n".join(lines)