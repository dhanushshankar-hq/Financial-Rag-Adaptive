import asyncio
from app.retrieval.parsers.docling_adapter import DoclingParserAdapter

async def run_test():
    parser = DoclingParserAdapter()
    result = await parser.parse_pdf(
        "data/raw/sample_report.pdf",
        metadata={"ticker": "TCS", "fiscal_year": "FY24"}
    )   
    print(f"File: {result.filename}")
    print(f"Tables Extracted: {len(result.tables)}")

    if result.tables:
        print("\n--- First Table Preview (Markdown) ---")
        print(result.tables[0].markdown_data[:500])

if __name__ == "__main__":
    asyncio.run(run_test())