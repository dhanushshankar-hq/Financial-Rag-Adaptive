import asyncio
from backend.app.retrieval.hybrid_retriever import HybridRetriever

async def main():
    retriever = HybridRetriever()
    query = "What does segment reporting says?"
    
    results = await retriever.retrieve(query, top_k=5)
    
    print(f"\nQuery: '{query}'\n")
    for idx, res in enumerate(results, 1):
        print(f"--- Result {idx} (RRF Score: {res['rrf_score']:.4f}) ---")
        print(f"Heading Path: {res['heading_path']}")
        print(f"Content Preview: {res['content'][:250]}...\n")

if __name__ == "__main__":
    asyncio.run(main())