import asyncio
from backend.app.ingestion.pipeline import IngestionPipeline

async def main():
    pipeline = IngestionPipeline()
    filing_id = await pipeline.ingest_filing(
        file_path="data/raw/nesle_fy24.pdf",
        company_name="Nesle",
        ticker="Nsle",
        fiscal_year="FY24"
    )
    print(f"Ingested Filing ID: {filing_id}")

if __name__ == "__main__":
    asyncio.run(main())