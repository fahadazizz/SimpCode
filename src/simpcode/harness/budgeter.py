from typing import List, Dict, Any
from pydantic import BaseModel

class ContextItem(BaseModel):
    id: str
    content: str
    priority: int # Lower is higher priority

class ContextBudgeter:
    def __init__(self, total_budget: int = 100000):
        self.total_budget = total_budget

    def _estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def assemble(self, mandatory: List[ContextItem], semantic: List[ContextItem], targeted: List[ContextItem]) -> str:
        all_items = sorted(mandatory, key=lambda x: x.priority)
        current_context = ""
        current_tokens = 0
        
        # Add mandatory first
        for item in all_items:
            current_context += f"--- {item.id} ---\n{item.content}\n\n"
            current_tokens += self._estimate_tokens(item.content)
            
        # Add semantic and targeted if budget allows
        optional_items = sorted(semantic + targeted, key=lambda x: x.priority)
        for item in optional_items:
            tokens = self._estimate_tokens(item.content)
            if current_tokens + tokens <= self.total_budget:
                current_context += f"--- {item.id} ---\n{item.content}\n\n"
                current_tokens += tokens
            else:
                # Warning could be logged here
                pass
                
        return current_context
