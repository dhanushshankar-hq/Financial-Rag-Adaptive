from neo4j import AsyncGraphDatabase
from backend.app.core.config import settings

class Neo4jDatabaseManager:
    _instance = None
    _driver = None

    def __new__(cls):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    async def close(self):
        if self._driver is not None:
            await self._driver.close()
            self._driver = None

    def connect(self):
        self._driver = AsyncGraphDatabase.driver(
                uri=settings.NEO4J_URI,
                auth=(settings.NEO4J_USER,settings.NEO4J_PASSWORD)
                        )

    async def get_session(self):
        if self._driver is None:
            raise RuntimeError("Database driver is closed or uninitialized.")
        async with self._driver.session() as session:
            yield session

neo4j_db = Neo4jDatabaseManager()