import json
import structlog
from sqlalchemy import text
from sentence_transformers import SentenceTransformer

from backend.app.core.db.postgres import postgres_db
from backend.app.ingestion.parsers.docling_adapter import DoclingParserAdapter
from backend.app.ingestion.chunkers.section_chunker import FinancialSectionChunker

logger = structlog.get_logger()

class IngestionPipeline:
    def __init__(self):
        self.parser = DoclingParserAdapter()
        self.chunker = FinancialSectionChunker(target_chunk_size=512, overlap=64)

        self.embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")

    async def ingest_filing(
        self, 
        file_path: str, 
        company_name: str, 
        ticker: str, 
        fiscal_year: str, 
        source_url: str = None
    ) -> str:
        logger.info("Starting ingestion pipeline", ticker=ticker, year=fiscal_year)
        
        parsed_doc = await self.parser.parse_pdf(
            file_path=file_path, 
            metadata={"ticker": ticker, "fiscal_year": fiscal_year}
        )

        chunks = self.chunker.chunk_document(
            markdown_text=parsed_doc.full_text_markdown,
            default_metadata={"company_name": company_name, "ticker": ticker, "fiscal_year": fiscal_year}
        )

        chunk_texts = [c.content for c in chunks]
        logger.info("Generating embeddings", count=len(chunk_texts))
        embeddings = self.embedding_model.encode(chunk_texts, show_progress_bar=False).tolist()


        async for session in postgres_db.get_session():
            filing_query = text("""
                INSERT INTO filings (company_name, ticker, fiscal_year, source_url)
                VALUES (:company_name, :ticker, :fiscal_year, :source_url)
                ON CONFLICT (ticker, fiscal_year) DO UPDATE 
                SET company_name = EXCLUDED.company_name, source_url = EXCLUDED.source_url
                RETURNING id;
            """)
            res = await session.execute(
                filing_query,
                {
                    "company_name": company_name,
                    "ticker": ticker,
                    "fiscal_year": fiscal_year,
                    "source_url": source_url
                }
            )
            filing_id = res.scalar_one()

            chunk_insert_query = text("""
                INSERT INTO chunks (filing_id, heading_path, chunk_index, content, token_count, embedding, metadata)
                VALUES (:filing_id, :heading_path, :chunk_index, :content, :token_count, :embedding, :metadata);
            """)

            chunk_records = []
            for idx, c in enumerate(chunks):
                chunk_records.append({
                    "filing_id": filing_id,
                    "heading_path": c.heading_path,
                    "chunk_index": c.chunk_index,
                    "content": c.content,
                    "token_count": c.token_count,
                    "embedding": str(embeddings[idx]),
                    "metadata": json.dumps(c.metadata)
                })

            await session.execute(chunk_insert_query, chunk_records)
            await session.commit()

        logger.info("Ingestion completed successfully", filing_id=str(filing_id), total_chunks=len(chunks))
        return str(filing_id)