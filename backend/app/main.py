from fastapi import FastAPI,status
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.core.logging import setup_logging
from sqlalchemy import text
import asyncio
import structlog
import time

from backend.app.core.db.neo4j import neo4j_db
from backend.app.core.db.postgres import postgres_db
from backend.app.core.db.redis import redis_db

setup_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info("Initializing database")
    neo4j_db.connect()
    redis_db.connect()

    yield

    logger.info("Closing database connections")
    await neo4j_db.close()
    await redis_db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

async def check_postgres():
    try:
        async for session in postgres_db.get_session():
            await session.execute(text('SELECT 1'))
            return 'Healthy'
    except Exception as e:
        logger.error("Postgres health check failed", error=str(e))
        return f"unhealthy: {str(e)}"

async def check_neo4j():
    try:
        async for session in neo4j_db.get_session():
            await session.run("RETURN 1")
            return 'Healthy'
    except Exception as e:
        logger.error("Neo4j health check failed", error=str(e))
        return f"unhealthy: {str(e)}"

async def check_redis():
    try:
        async for session in redis_db.get_session():
            await session.ping()
            return 'Healthy'
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        return f"unhealthy: {str(e)}"

@app.get('/health',tags=['health'])
async def health_check():
    start_time = time.perf_counter()
    pg_status,neo_status,redis_status = await asyncio.gather(
        check_postgres(),
        check_neo4j(),
        check_redis()
    )
    latency_ms = round(((time.perf_counter() - start_time)*1000),2)
    all_healthy = all(s == 'Healthy' for s in [pg_status,neo_status,redis_status])
    response_body =  {
        "status" : "healthy" if all_healthy else "unhealthy",
        "latency_ms":latency_ms,
        "project" : settings.PROJECT_NAME,
        "version" : "1.0.0"
    }
    http_status = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(content=response_body,status_code=http_status)


if __name__ == "__main__":
    asyncio.run(health_check())