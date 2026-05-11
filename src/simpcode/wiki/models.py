import yaml
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from pathlib import Path

class SourceReference(BaseModel):
    file_path: str
    hash: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None

class WikiPageMetadata(BaseModel):
    id: str
    type: str  # cognitive, structural, module, symbol, decision, change
    sources: List[SourceReference] = []
    last_updated: float
    title: Optional[str] = None

class WikiPage(BaseModel):
    metadata: WikiPageMetadata
    content: str

    @classmethod
    def from_file(cls, file_path: Path) -> "WikiPage":
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
        
        if not raw_text.startswith("---"):
            raise ValueError(f"Invalid wiki page format: {file_path}")
            
        parts = raw_text.split("---", 2)
        if len(parts) < 3:
            raise ValueError(f"Invalid wiki page format: {file_path}")
            
        yaml_content = parts[1]
        body_content = parts[2].strip()
        
        metadata_dict = yaml.safe_load(yaml_content)
        metadata = WikiPageMetadata(**metadata_dict)
        
        return cls(metadata=metadata, content=body_content)

    def to_file(self, file_path: Path):
        metadata_yaml = yaml.dump(self.metadata.model_dump(), sort_keys=False)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"---\n{metadata_yaml}---\n\n{self.content}")
