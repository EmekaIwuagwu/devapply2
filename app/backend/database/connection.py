from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings


def _make_async_url(url: str) -> str:
    """
    SQLAlchemy async engine requires asyncpg driver.
    Render/Heroku provide  postgresql://  — upgrade it to  postgresql+asyncpg://
    """
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


# Register uuid.UUID → str adapter for SQLite so that Python uuid objects
# can be used as bind parameters in WHERE clauses without InterfaceError.
def _register_sqlite_uuid_adapter():
    try:
        import sqlite3
        import uuid
        sqlite3.register_adapter(uuid.UUID, str)
    except Exception:
        pass


_register_sqlite_uuid_adapter()

# For async transactions
engine = create_async_engine(
    _make_async_url(settings.DATABASE_URL),
    echo=settings.DATABASE_ECHO,
)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

