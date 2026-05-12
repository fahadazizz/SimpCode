from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel
from simpcode.core.analyzer import ProjectMetadata
from simpcode.core.llm import LLMClient
from simpcode.core.prompts import registry

class SynthesizedDocs(BaseModel):
    simp_md: str
    spec_md: str

class IntelligenceSynthesizer:
    """
    SimpCode Onboarding Architect: Uses LLM to synthesize project understanding and rules.
    """
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def synthesize(self, metadata: ProjectMetadata) -> SynthesizedDocs:
        system_instruction = registry.load("onboarding_architect")
        prompt = registry.load("onboarding_documents", include_base=False).format(
            project_name=metadata.name,
            file_tree=metadata.file_tree,
            manifests=metadata.manifests,
            entry_point_samples=metadata.entry_point_samples,
        )
        return self.llm.structured_output(prompt, SynthesizedDocs, system_instruction)

class DocumentGenerator:
    """
    Handles physical writing of synthesized documents.
    """
    def __init__(self, root: Path):
        self.root = root

    def write_docs(self, docs: SynthesizedDocs):
        simp_content = docs.simp_md.strip()
        spec_content = docs.spec_md.strip()
        
        # Ensure SIMP.md always has content; SPEC.md is optional.
        if not simp_content:
            simp_content = "# Project Manifest (SIMP)\n\nAuto-generated structure."

        (self.root / "SIMP.md").write_text(simp_content + "\n")

        if spec_content:
            (self.root / "SPEC.md").write_text(spec_content + "\n")
        else:
            spec_path = self.root / "SPEC.md"
            if spec_path.exists():
                spec_path.unlink()
