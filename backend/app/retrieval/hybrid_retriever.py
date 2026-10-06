from typing import List, Dict, Any
import structlog
from backend.app.retrieval.vector_search import VectorSearcher
from backend.app.retrieval.bm25_search import SparseSearcher
import asyncio


logger = structlog.get_logger()

class HybridRetriever:
    def __init__(self, k_constant: int = 60):
        self.vector_searcher = VectorSearcher()
        self.sparse_searcher = SparseSearcher()
        self.k = k_constant

    async def retrieve(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:

        candidate_pool_size = top_k * 2

        logger.info("Executing hybrid search", query=query)
        
        dense_results, sparse_results = await asyncio.gather(
            self.vector_searcher.search(query, top_k=candidate_pool_size),
            self.sparse_searcher.search(query, top_k=candidate_pool_size)
        )

        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(dense_results, start=1):
            chunk_id = str(item["id"])
            chunk_map[chunk_id] = item
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (self.k + rank))

        for rank, item in enumerate(sparse_results, start=1):
            chunk_id = str(item["id"])
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = item
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (self.k + rank))

        sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        final_results = []
        for chunk_id, score in sorted_chunks[:top_k]:
            chunk = chunk_map[chunk_id]
            chunk["rrf_score"] = score
            final_results.append(chunk)

        logger.info("Hybrid search completed", retrieved_count=len(final_results))
        return final_results