from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import tiktoken

class ContextItem(BaseModel):
    id: str
    content: str
    priority: int # Lower is higher priority

class ContextBudgeter:
    """
    Manages the context window by enforcing token limits.
    Uses tiktoken for accurate counting.
    """
    def __init__(self, total_budget: int = 100000, model: str = "gpt-4"):
        self.total_budget = total_budget
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except Exception:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def assemble(self, mandatory: List[ContextItem], semantic: List[ContextItem], targeted: List[ContextItem]) -> str:
        """
        Assembles context based on priority and budget.
        Priority: Mandatory > Semantic > Targeted
        """
        assembled_content = []
        current_tokens = 0
        
        # 1. Load Baseline Context (SIMP.md, index.md, optional SPEC.md)
        # Baseline items are NEVER dropped per Spec 14.1
        mandatory_sorted = sorted(mandatory, key=lambda x: x.priority)
        for item in mandatory_sorted:
            header = f"--- MANDATORY: {item.id} ---\n"
            content = item.content + "\n\n"
            assembled_content.append(header + content)
            current_tokens += self.count_tokens(header + content)

        if current_tokens > self.total_budget:
            warning = (
                "\n[SYSTEM WARNING: Mandatory context alone exceeds the total budget. "
                "No mandatory items were dropped, but optional context will be omitted.]\n"
            )
            assembled_content.append(warning)
            print("[Warning] Mandatory context exceeds total budget; optional context will be dropped.")

        # 2. Load Optional (Semantic Wiki pages and Targeted Code ranges)
        optional_items = sorted(semantic + targeted, key=lambda x: x.priority)
        
        for item in optional_items:
            header = f"--- {item.id} ---\n"
            content = item.content + "\n\n"
            tokens = self.count_tokens(header + content)
            
            if current_tokens + tokens <= self.total_budget:
                assembled_content.append(header + content)
                current_tokens += tokens
            else:
                dropped_msg = f"\n[SYSTEM WARNING: Context Budget Exceeded - Dropped Module/Code: {item.id}]\n"
                assembled_content.append(dropped_msg)
                current_tokens += self.count_tokens(dropped_msg)
                print(f"[Warning] Context Budget Exceeded: Dropping {item.id}")
                
        return "".join(assembled_content)
