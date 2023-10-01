from multiprocessing import cpu_count

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

# ---------------------------------------------------------------------------
DB_POOL_SIZE = 50
WEB_CONCURRENCY = cpu_count()
POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)
# ---------------------------------------------------------------------------
engine = create_async_engine(
    str(settings.DATABASE_URL),
    future=True,
    pool_size=POOL_SIZE,
    max_overflow=64,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
