from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


_engine = None


async def _get_engine():
    global _engine
    if _engine is not None:
        return _engine

    from app.config import settings

    if settings.database_url:
        # Local development: direct connection
        _engine = create_async_engine(settings.database_url, echo=False)
    else:
        # Cloud Run: Cloud SQL connector
        from google.cloud.sql.connector import create_async_connector
        connector = await create_async_connector()

        async def get_conn():
            return await connector.connect_async(
                settings.cloud_sql_connection_name,
                "asyncpg",
                user=settings.db_user,
                password=settings.db_password,
                db=settings.db_name,
            )

        _engine = create_async_engine(
            "postgresql+asyncpg://",
            async_creator=get_conn,
            echo=False,
        )

    return _engine


async def get_db() -> AsyncSession:
    engine = await _get_engine()
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
