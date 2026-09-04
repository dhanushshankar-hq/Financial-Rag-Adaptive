from abc import ABC, abstractmethod
from pydantic import BaseModel,Field
from typing import List, Dict, Any, Optional

class ExtractedTable(BaseModel):
    page_number : int
    csv_data : str
    markdown_data :str

class ParsedDocument(BaseModel):
    filename : str
    total_pages : int
    full_text_markdown : str
    table : List[ExtractedTable] = Field(default_factory=list)
    metadata : Dict[str,Any] = Field(defualt_factory=list)

class IDocumentParser(ABC):
    @abstractmethod
    async def parse_pdf(self,file_path:str,metadata:Optional[Dict[str,Any]] = None) -> ParsedDocument:
        pass
