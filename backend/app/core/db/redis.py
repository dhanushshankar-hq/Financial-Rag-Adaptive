import redis.asyncio as redis
from backend.app.core.config import settings
class RedisManager:
    _instance = None
    _pool = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.aclose()

    def connect(self):
        if self._pool is None:
            self._pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                username=settings.REDIS_USERNAME,
                password=settings.REDIS_PASSWORD,
                max_connections=10,
                decode_responses=True 
            )

    async def get_session(self):
        if self._pool is None:
            raise RuntimeError("Database driver is closed or uninitialized.")
        async with redis.Redis(connection_pool=self._pool) as session:
            yield session

redis_db = RedisManager()