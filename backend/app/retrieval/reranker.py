from typing import List, Dict, Any
import structlog
from sentence_transformers import CrossEncoder

logger = structlog.get_logger()

class CrossEncoderReranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        logger.info("Initializing Cross-Encoder re-ranker", model=model_name)
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        logger.info("Re-ranking candidates with Cross-Encoder", candidate_count=len(candidates))

        pairs = [[query, candidate["content"]] for candidate in candidates]

        scores = self.model.predict(pairs, show_progress_bar=False)

        for idx, candidate in enumerate(candidates):
            candidate["rerank_score"] = float(scores[idx])

        sorted_candidates = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

        final_results = sorted_candidates[:top_k]
        logger.info("Re-ranking complete", selected_count=len(final_results))
        return final_results