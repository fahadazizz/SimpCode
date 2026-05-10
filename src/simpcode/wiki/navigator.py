from typing import List
from pydantic import BaseModel
from simpcode.core.llm import LLMClient

class NavigationDecision(BaseModel):
    pages_to_load: List[str]
    rationale: str

class WikiNavigator:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def navigate(self, task: str, index_content: str) -> NavigationDecision:
        system_instruction = """You are the Wiki Navigator for SimpCode.
Your job is to read the project index and decide which Wiki pages are most relevant to the user's task.
Output your decision as a JSON object with:
- pages_to_load: a list of page IDs (e.g., ["invariants", "modules/auth"])
- rationale: why you chose these pages.
"""
        prompt = f"User Task: {task}\n\nProject Index:\n{index_content}"
        
        result = self.llm.structured_output(prompt, NavigationDecision, system_instruction)
        return NavigationDecision(**result)
