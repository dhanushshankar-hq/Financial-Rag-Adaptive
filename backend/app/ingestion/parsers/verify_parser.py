import asyncio
from backend.app.ingestion.parsers.docling_adapter import DoclingAdapter

async def run_test():
    parser = DoclingAdapter()
    result = await parser.parse_pdf(
        "data/raw/tcs_fy25.pdf",
        metadata={"ticker": "TCS", "fiscal_year": "FY25"}
    )   
    print(f"File: {result.filename}")
    print(f"Tables Extracted: {len(result.tables)}")

    if result.tables:
        print("\n--- First Table Preview (Markdown) ---")
        print(result.tables[100].markdown_data[:500])

if __name__ == "__main__":
    asyncio.run(run_test())