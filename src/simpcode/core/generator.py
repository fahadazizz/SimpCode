from pathlib import Path
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
        constitution = registry.load("simp_constitution", include_base=False)
        
        prompt = registry.load("onboarding_documents", include_base=False).format(
            project_name=metadata.name,
            file_tree=metadata.file_tree,
            manifests=metadata.manifests,
            entry_point_samples=metadata.entry_point_samples,
            constitution=constitution
        )
        return self.llm.structured_output(prompt, SynthesizedDocs, system_instruction)


class DocumentGenerator:
    """
    Handles physical writing of synthesized documents.
    """

    def __init__(self, root: Path):
        self.root = root

    def write_docs(self, docs: SynthesizedDocs, overwrite_spec: bool = False):
        spec_content = docs.spec_md.strip()

        if spec_content:
            (self.root / "SPEC.md").write_text(spec_content + "\n")
        elif overwrite_spec:
            spec_path = self.root / "SPEC.md"
            if spec_path.exists():
                spec_path.unlink()
