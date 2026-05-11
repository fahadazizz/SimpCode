from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel
from simpcode.core.analyzer import ProjectMetadata
from simpcode.core.llm import LLMClient
from simpcode.core.prompts import registry

class SynthesizedDocs(BaseModel):
    simp_md: str
    agent_md: str

class IntelligenceSynthesizer:
    """
    SimpCode Onboarding Architect: Uses LLM to synthesize project understanding and rules.
    """
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def synthesize(self, metadata: ProjectMetadata) -> SynthesizedDocs:
        system_instruction = registry.load("onboarding_architect")
        prompt = f"""Raw Project Metadata:
Project Name: {metadata.name}
File Tree: {metadata.file_tree}

Manifests:
{metadata.manifests}

Entry Point Samples:
{metadata.entry_point_samples}

Synthesize the SIMP.md and AGENT.md content.
"""
        return self.llm.structured_output(prompt, SynthesizedDocs, system_instruction)

class DocumentGenerator:
    """
    Handles physical writing of synthesized documents.
    """
    def __init__(self, root: Path):
        self.root = root

    def write_docs(self, docs: SynthesizedDocs):
        (self.root / "SIMP.md").write_text(docs.simp_md)
        (self.root / "AGENT.md").write_text(docs.agent_md)
