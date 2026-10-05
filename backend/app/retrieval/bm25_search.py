from sqlalchemy import text
from app.core.db.postgres import postgres_db

class SparseSearcher:
    async def search(self, query: str, top_k: int = 20) -> list[dict]:
        async for session in postgres_db.get_session():
            result = await session.execute(
                text("""
                    SELECT id, filing_id, heading_path, content, metadata,
                           ts_rank_cd(to_tsvector('english', content), plainto_tsquery('english', :query)) AS score
                    FROM chunks
                    WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :query)
                    ORDER BY score DESC
                    LIMIT :top_k;
                """),
                {"query": query, "top_k": top_k}
            )
            rows = result.mappings().all()
            return [dict(row) for row in rows]