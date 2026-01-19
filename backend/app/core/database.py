"""
Database connection and Supabase client initialization.
"""
from supabase import create_client, Client
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import get_settings

settings = get_settings()

# Supabase Client (for Auth, Storage, Realtime)
supabase: Client | None = None

def get_supabase_client() -> Client:
    """Get or create Supabase client."""
    global supabase
    if supabase is None and settings.supabase_url and settings.supabase_key:
        supabase = create_client(settings.supabase_url, settings.supabase_key)
    return supabase

# SQLAlchemy Async Engine (for direct PostgreSQL access)
# Convert postgres:// to postgresql+asyncpg://
async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://") if settings.database_url else ""

engine = create_async_engine(
    async_database_url,
    echo=settings.debug,
    future=True
) if async_database_url else None

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
) if engine else None

Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not configured")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
