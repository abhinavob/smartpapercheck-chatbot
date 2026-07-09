from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

# Supabase's connection pooler (pgbouncer, transaction mode) does not support the prepared
# statements asyncpg uses by default, so disable them outside local development.
connect_args: dict[str, int] = {}
if settings.environment != "local":
    connect_args["statement_cache_size"] = 0

engine = create_async_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
