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
        simp_content = docs.simp_md.strip()
        agent_content = docs.agent_md.strip()
        
        # Ensure we always have content
        if not simp_content:
            simp_content = "# Project Manifest (SIMP)\n\nAuto-generated structure."
        if not agent_content:
            agent_content = "# SimpCode Agent Policy\n\n1. Read before write.\n2. Ensure tests pass."

        (self.root / "SIMP.md").write_text(simp_content + "\n")
        (self.root / "AGENT.md").write_text(agent_content + "\n")
