from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.app.core.config import settings

class PostgresManager:
    """
    Singleton manager for asynchronous PostgreSQL database connections.
    Handles the engine lifecycle and session generation for the application.
    """
    _instance = None

    def __new__(cls):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
            cls._instance.engine = create_async_engine(
                url=settings.ASYNC_POSTGRES_URI,
                echo = False,
                pool_size = 10,
                max_overflow = 20
            )
            cls._instance.session_factory = async_sessionmaker(
                bind=cls._instance.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

        return cls._instance
    
    async def get_session(self):
        """
        Yields an asynchronous database session.
        Usage: async with postgres_db.get_session() as session:
        """
        async with self.session_factory() as session:
            yield session

postgres_db = PostgresManager()
