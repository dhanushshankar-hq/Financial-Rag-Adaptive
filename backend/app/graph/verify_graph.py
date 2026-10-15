import asyncio
from backend.app.graph.extractor import MetricExtractor
from backend.app.graph.loader import Neo4jGraphLoader
from backend.app.core.db.neo4j import neo4j_db


async def main():
    sample_markdown = """
| Particulars | FY24 (INR Crores) |
|---|---|
| Revenue from Operations | 240893 |
| Operating Profit | 59124 |
| Net Profit | 49521 |
    """
    neo4j_db.connect()

    extractor = MetricExtractor()
    metrics = extractor.extract_from_table(sample_markdown)
    
    loader = Neo4jGraphLoader()
    await loader.load_metrics(
        company_name="Tata Consultancy Services",
        ticker="TCS",
        fiscal_year="FY24",
        metrics=metrics
    )

    await neo4j_db.close()
    print("Neo4j graph metrics successfully populated and verified.")

if __name__ == "__main__":
    asyncio.run(main())