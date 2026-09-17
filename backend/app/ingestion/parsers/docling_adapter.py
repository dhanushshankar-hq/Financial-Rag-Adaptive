from backend.app.core.logging import setup_logging
from backend.app.ingestion.parsers.base import IDocumentParser,ParsedDocument,ExtractedTable
from typing import Optional,Dict,Any
from docling.document_converter import DocumentConverter
from pathlib import Path
import asyncio
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
import structlog

logger = structlog.get_logger()

class DoclingAdapter(IDocumentParser):
    def __init__(self):
        self._converter :DocumentConverter =  None

    @property
    def converter(self) -> DocumentConverter:
        if self._converter == None:
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = False
            self._converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
        return self._converter

    async def parse_pdf(self,file_path:str, metadata:Optional[Dict[str,Any]] = None) -> ParsedDocument:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Filing PDF not found at: {file_path}")

        logger.info("Starting layout-aware PDF parsing", file=path.name)

        loop = asyncio.get_running_loop()

        conv_res = await loop.run_in_executor(
            None, lambda: self.converter.convert(str(path))
        )

        doc = conv_res.document
        markdown_content = doc.export_to_markdown()

        extracted_tables = []

        for table in doc.tables:
            page_no = table.prov[0].page_no if table.prov else 1
            try:
                df = table.export_to_dataframe(doc=doc)
                extracted_tables.append(
                ExtractedTable(
                    page_number=page_no,
                    csv_data=df.to_csv(),
                    markdown_data=df.to_markdown(index=False)
                )
                )
            except Exception as e:
                logger.warning("Failed to export table dataframe", page=page_no, error=str(e))

        logger.info(
            "PDF parsing complete",
            file=path.name,
            tables_found=len(extracted_tables)
            )

        return ParsedDocument(
            filename=path.name,
            total_pages=len(doc.pages) if hasattr(doc, "pages") else 1,
            full_text_markdown=markdown_content,
            tables=extracted_tables,
            metadata=metadata or {}
            )






    


