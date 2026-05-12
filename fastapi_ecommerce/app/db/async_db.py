"""
Asynchronous Database Module

This module handles ALL asynchronous database operations:
- Creating the async engine (aiomysql driver)
- Creating the async session factory
- Providing async sessions for FastAPI endpoints

Use this module for:
- ALL FastAPI endpoint database operations
- Any I/O-bound database work during request handling

DO NOT use sync sessions for API requests.
Async sessions allow the event loop to handle other requests
while waiting for the database to respond.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from app.config.settings import settings
from app.utils.loggers import logger


# ============================================
# ASYNCHRONOUS DATABASE URL
# ============================================

"""
The async URL uses the 'aiomysql' driver.
Format: mysql+aiomysql://user:password@host:port/database

aiomysql is an ASYNCHRONOUS MySQL driver.
It's built on top of asyncio (Python's async library).

How aiomysql differs from pymysql:
┌─────────────────────────────────────────────────────────────┐
│                  ASYNC vs SYNC DRIVERS                       │
│                                                              │
│  pymysql (SYNC):                                             │
│  engine.execute("SELECT ...")                                │
│  → Thread BLOCKS until MySQL responds                       │
│  → While blocked: thread does NOTHING                       │
│                                                              │
│  aiomysql (ASYNC):                                          │
│  await session.execute(select(...))                          │
│  → Coroutine YIELDS control                                 │
│  → Event loop works on OTHER requests                       │
│  → When MySQL responds: coroutine RESUMES                   │
│  → Same thread, but handles THOUSANDS of requests           │
└─────────────────────────────────────────────────────────────┘
"""

ASYNC_DATABASE_URL: str = (
    f"mysql+aiomysql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
    f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
)


# ============================================
# ASYNCHRONOUS ENGINE
# ============================================

"""
The async engine manages a pool of NON-BLOCKING connections.

Under the hood:
┌─────────────────────────────────────────────────────────┐
│                   ASYNC ENGINE                           │
│                                                          │
│  Connection Pool (pool_size=10)                         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐         │
│  │Conn 1│ │Conn 2│ │Conn 3│ │Conn 4│ │ ...  │         │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘         │
│     │        │        │        │        │               │
│     │   Each connection uses aiomysql                    │
│     │   Queries are sent via asyncio event loop          │
│     │   While waiting: OTHER work happens                │
│     │                                                   │
│     └────────────┬──────────────┘                      │
│                  ▼                                       │
│            MySQL Server                                  │
└─────────────────────────────────────────────────────────┘
"""

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=True,
)


# ============================================
# ASYNCHRONOUS SESSION FACTORY
# ============================================

"""
AsyncSessionLocal creates AsyncSession objects.

Key difference from sync:
- expire_on_commit=False: Don't expire objects after commit
  (Sync sessions auto-expire; async sessions need this explicit)

Why expire_on_commit=False?
- In sync: After commit, accessing attributes triggers a lazy load
- In async: Lazy loading doesn't work well (would need await)
- Setting to False keeps objects usable after commit
"""

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ============================================
# DEPENDENCY: GET ASYNC SESSION
# ============================================

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an ASYNCHRONOUS database session for FastAPI endpoints.
    
    THIS IS THE PRIMARY SESSION FOR ALL API REQUESTS.
    
    Lifecycle:
    1. session = AsyncSessionLocal()   ← Get connection from pool
    2. yield session                    ← Give to endpoint
    3. await session.close()           ← Return connection to pool
    
    Usage in endpoints:
    
        @router.get("/products")
        async def get_products(
            session: AsyncSession = Depends(get_async_session)
        ):
            result = await session.execute(select(Product))
            return result.scalars().all()
    
    Why async?
    - Every 'await session.execute()' yields control
    - 1000 requests can share the same thread
    - While one request waits for MySQL, others make progress
    
    Yields:
        AsyncSession: A SQLAlchemy AsyncSession object
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        # Always close the session
        # This returns the connection to the pool
        await session.close()


# ============================================
# DEPENDENCY: ASYNC SESSION WITH COMMIT
# ============================================

async def get_async_session_with_commit() -> AsyncGenerator[AsyncSession, None]:
    """
    Same as get_async_session, but auto-commits on success.
    
    Use this for endpoints that MODIFY data (POST, PUT, DELETE).
    If the endpoint succeeds, changes are committed automatically.
    If an error occurs, changes are rolled back.
    
    Usage:
        @router.post("/products")
        async def create_product(
            data: ProductCreate,
            session: AsyncSession = Depends(get_async_session_with_commit)
        ):
            product = Product(**data.model_dump())
            session.add(product)
            # No need to call commit() - it's automatic!
            return product
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
        logger.debug("Database changes committed")
    except Exception:
        await session.rollback()
        logger.error("Database changes rolled back due to error")
        raise
    finally:
        await session.close()



