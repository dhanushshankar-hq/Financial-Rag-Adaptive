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
);

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
CREATE INDEX IF NOT EXISTS idx_chunks_section_type ON chunks(section_type);

CREATE TABLE IF NOT EXISTS model_pricing (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
model_name TEXT UNIQUE NOT NULL,
provider TEXT NOT NULL,
input_cost_per_1k_tokens NUMERIC(10,6) NOT NULL,
output_cost_per_1k_tokens NUMERIC(10,6) NOT NULL,
updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO model_pricing (model_name,provider,input_cost_per_1k_tokens,output_cost_per_1k_tokens)
VALUES 
('llama-3.3-70b-versatile', 'Groq', 0.000590, 0.000790),
('gemini-2.5-flash', 'Google', 0.000075, 0.000300)
ON CONFLICT (model_name) DO NOTHING;

CREATE TABLE IF NOT EXISTS query_logs (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
query_text TEXT NOT NULL,
router_decision TEXT NOT NULL,
router_model TEXT,
generator_model TEXT,
prompt_tokens INT DEFAULT 0,
completion_tokens INT DEFAULT 0,
retrieved_chunk_ids UUID[],
self_correction_iterations INT DEFAULT 0,
total_latency_ms FLOAT NOT NULL,
llm_cost_usd NUMERIC(10,6) DEFAULT 0.0,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_feedback (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
query_id UUID NOT NULL REFERENCES query_logs(id) ON DELETE CASCADE,
rating INT CHECK (rating IN (-1,1)),
feedback_text TEXT,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""