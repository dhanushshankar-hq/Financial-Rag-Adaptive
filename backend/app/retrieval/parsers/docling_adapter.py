from backend.app.core.logging import setup_logging
from backend.app.retrieval.parsers.base import IDocumentParser,ParsedDocument
from typing import Optional,Dict,Any
from docling.document_converter import DocumentConverter
from pathlib import Path
import asyncio

logger = setup_logging()

class DoclingAdapter(IDocumentParser):
    def __init__(self):
        self._converter :DocumentConverter =  None

    @property
    def converter(self) -> DocumentConverter:
        if self._converter == None:
            self._converter = DocumentConverter
        return self._converter

    async def pdf_parse(self,file_path:str, metedata:Optional[Dict[str,Any]] = None) -> ParsedDocument:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Filing PDF not found at: {file_path}")

        logger.info("Starting layout-aware PDF parsing", file=path.name)

        loop = asyncio.get_event_loop()

        conv_res = await loop.run_in_executor(
            None, lambda: self.converter.convert(str(path))
        )

        doc = conv_res.document
        markdown_content = doc.export_to_markdown()

        extracted_table = []

        for table in doc.tables:
            



    


