from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import get_settings

settings = get_settings()

# Async Engine - PostgreSQL এর জন্য
# NullPool use করছি কারণ async context এ connection pooling different
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL queries log করবে debug mode এ
    poolclass=NullPool,
    future=True
)

# Session Factory - প্রতিটা request এ নতুন session তৈরি করবে
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Object গুলো session close এর পরেও accessible থাকবে
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()

# Dependency - FastAPI route এ inject করবো
async def get_db() -> AsyncSession:
    """
    Database session dependency
    প্রতিটা request এ একটা session create হবে
    Request শেষে automatically close হবে
    
    Usage in route:
    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """
    Database tables create করবে
    Application startup এ call করতে হবে
    """
    async with engine.begin() as conn:
        # All tables create করবে যদি না থাকে
        await conn.run_sync(Base.metadata.create_all)