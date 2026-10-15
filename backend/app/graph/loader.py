import structlog
from typing import List
from backend.app.core.db.neo4j import neo4j_db
from backend.app.graph.extractor import FinancialMetric

logger = structlog.get_logger()

class Neo4jGraphLoader:
    async def load_metrics(
        self, 
        company_name: str, 
        ticker: str, 
        fiscal_year: str, 
        metrics: List[FinancialMetric]
    ):
        logger.info("Loading financial metrics into Neo4j graph", ticker=ticker, year=fiscal_year)

        
        async for session in neo4j_db.get_session():
            cypher_base = """
            MERGE (c:Company {ticker: $ticker})
            ON CREATE SET c.name = $company_name
            MERGE (f:FiscalYear {year: $fiscal_year})
            MERGE (c)-[:FILED]->(f)
            """
            await session.run(cypher_base, {"ticker": ticker, "company_name": company_name, "fiscal_year": fiscal_year})

            for m in metrics:
                cypher_metric = """
                MATCH (c:Company {ticker: $ticker})-[:FILED]->(f:FiscalYear {year: $fiscal_year})
                MERGE (m:Metric {name: $name, company: $ticker, year: $fiscal_year})
                SET m.raw_value = $raw_value,
                    m.currency = $currency,
                    m.scale = $scale
                MERGE (f)-[:HAS_METRIC]->(m)
                """
                await session.run(
                    cypher_metric,
                    {
                        "ticker": ticker,
                        "fiscal_year": fiscal_year,
                        "name": m.metric_name,
                        "raw_value": m.raw_value,
                        "currency": m.currency,
                        "scale": m.scale
                    }
                )

        logger.info("Graph metrics loaded successfully", count=len(metrics))