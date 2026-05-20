import asyncio
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


_engine = None
_session_factory = None
_connector = None  # Cloud SQL connector — stored so it can be closed at shutdown
_engine_lock = asyncio.Lock()


async def _get_engine():
    global _engine, _session_factory, _connector
    async with _engine_lock:
        if _engine is not None:
            return _engine

        from app.config import settings

        if settings.database_url:
            _engine = create_async_engine(settings.database_url, echo=False)
        else:
            # Cloud Run: Cloud SQL connector
            from google.cloud.sql.connector import create_async_connector
            _connector = await create_async_connector()

            async def get_conn():
                return await _connector.connect_async(
                    settings.cloud_sql_connection_name,
                    "asyncpg",
                    user=settings.db_user,
                    password=settings.db_password,
                    db=settings.db_name,
                )

            _engine = create_async_engine(
                "postgresql+asyncpg://",  # URL ignored; async_creator supplies the real connection
                async_creator=get_conn,
                echo=False,
            )

        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    await _get_engine()
    async with _session_factory() as session:
        yield session


async def close_db() -> None:
    """Close the engine and Cloud SQL connector. Call from app lifespan shutdown."""
    global _engine, _session_factory, _connector
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
    if _connector is not None:
        await _connector.close_async()
        _connector = None
