from typing import List
from pydantic import BaseModel
from simpcode.core.llm import LLMClient
from simpcode.core.prompts import registry

class NavigationDecision(BaseModel):
    pages_to_load: List[str]
    rationale: str
    missing_context: List[str] # Topics not covered by current Wiki but needed

class WikiNavigator:
    """
    SimpCode Navigator: Uses the Project Index to strategically select Wiki nodes.
    Replaces probabilistic RAG with intentional, reasoning-based navigation.
    """
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def navigate(self, task: str, index_content: str) -> NavigationDecision:
        system_instruction = registry.load("wiki_navigator")
        prompt = registry.load("wiki_navigation", include_base=False).format(
            task=task,
            index_content=index_content,
        )
        return self.llm.structured_output(prompt, NavigationDecision, system_instruction)
