from backend.app.core.db.postgres import postgres_db
from backend.app.core.db.neo4j import neo4j_db
from backend.app.core.db.redis import redis_db
import structlog

logger = structlog.get_logger()

postgres_dll = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS filings (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
company_name TEXT NOT NULL,
ticker TEXT NOT NULL,
fiscal_year TEXT NOT NULL,
source_url TEXT,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
)

CREATE TABLE IF NOT EXISTS chunks (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
filings_id UUID NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
section_type TEXT NOT NULL,
chunk_index INT NOT NULL,
content TEXT NOT NULL,
token_count INT NOT NULL,
embedding vector(1024),
metadata JSONB DEFAULLT '{}'::jsonb,
created_at TiMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chunks_filing_id ON chunks(filing_id);
CREATE INDEX IF NOT EXISTS idx_chunks_section_type ON chunks(section_type)
"""