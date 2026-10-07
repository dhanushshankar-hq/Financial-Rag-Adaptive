from typing import List, Dict, Any
import structlog
from backend.app.retrieval.hybrid_retriever import HybridRetriever
from backend.app.retrieval.reranker import CrossEncoderReranker

logger = structlog.get_logger()

class RetrievalPipeline:
    def __init__(self):
        self.hybrid_retriever = HybridRetriever(k_constant=60)
        self.reranker = CrossEncoderReranker(model_name="BAAI/bge-reranker-base")

    async def search(self, query: str, candidate_pool_size: int = 20, top_k: int = 5) -> List[Dict[str, Any]]:
        logger.info("Starting end-to-end retrieval pipeline", query=query)

        candidates = await self.hybrid_retriever.retrieve(query, top_k=candidate_pool_size)

        if not candidates:
            logger.warning("No candidates found from hybrid search", query=query)
            return []
        
        final_results = self.reranker.rerank(query=query, candidates=candidates, top_k=top_k)

        logger.info("Retrieval pipeline execution finished", final_results_count=len(final_results))
        return final_results