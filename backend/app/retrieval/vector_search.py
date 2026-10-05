from sqlalchemy import text
from sentence_transformers import SentenceTransformer
from app.core.db.postgres import postgres_db

class VectorSearcher:
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-large-en-v1.5")

    async def search(self, query: str, top_k: int = 20) -> list[dict]:
        query_embedding = self.model.encode(query).tolist()
        
        async for session in postgres_db.get_session():
            result = await session.execute(
                text("""
                    SELECT id, filing_id, heading_path, content, metadata,
                           1 - (embedding <=> :query_embedding::vector) AS score
                    FROM chunks
                    ORDER BY embedding <=> :query_embedding::vector
                    LIMIT :top_k;
                """),
                {"query_embedding": str(query_embedding), "top_k": top_k}
            )
            rows = result.mappings().all()
            return [dict(row) for row in rows]