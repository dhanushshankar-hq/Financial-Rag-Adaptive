import asyncio
from backend.app.retrieval.pipeline import RetrievalPipeline

async def main():
    pipeline = RetrievalPipeline()
    query = "What does segment reporting says?"
    
    results = await pipeline.search(query, candidate_pool_size=10, top_k=3)
    
    print(f"\nQuery: '{query}'\n")
    for idx, res in enumerate(results, 1):
        print(f"=== Result {idx} ===")
        print(f"Heading Path: {res['heading_path']}")
        print(f"Hybrid RRF Score: {res.get('rrf_score', 0):.4f}")
        print(f"Cross-Encoder Score: {res.get('rerank_score', 0):.4f}")
        print(f"Content Snippet:\n{res['content'][:350]}...\n")

if __name__ == "__main__":
    asyncio.run(main())