"""
Database Module - SQLAlchemy 2.0 Async + Sync

This module provides:
1. Sync engine: For table creation and migrations
2. Async engine: For handling API requests
3. Sync session factory: For operations that need sync
4. Async session factory: For FastAPI endpoint dependencies
5. Base class: For ORM model definitions

Architecture:
┌──────────────────┐     ┌──────────────────┐
│   SYNC ENGINE    │     │  ASYNC ENGINE    │
│   (pymysql)      │     │  (aiomysql)      │
│   For table      │     │  For request     │
│   creation       │     │  handling        │
└──────────────────┘     └──────────────────┘
        │                        │
        │                        │
        ▼                        ▼
┌──────────────────────────────────────────┐
│           MySQL Database                 │
└──────────────────────────────────────────┘
"""

from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from app.config.settings import settings


# ============================================
# SYNCHRONOUS DATABASE URL
# ============================================

"""
The synchronous URL uses 'pymysql' driver.
Used for:
- Creating tables (SQLAlchemy's create_all is synchronous)
- Any operation where async isn't needed
"""
SYNC_DATABASE_URL: str = (
    f"mysql+pymysql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
    f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
)


# ============================================
# ASYNCHRONOUS DATABASE URL
# ============================================

"""
The asynchronous URL uses 'aiomysql' driver.
Used for:
- All API request handling
- Any I/O-bound database operations during requests
"""
ASYNC_DATABASE_URL: str = (
    f"mysql+aiomysql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
    f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
)


# ============================================
# SYNCHRONOUS ENGINE
# ============================================

"""
The sync engine manages a pool of BLOCKING database connections.

Under the hood:
- Uses pymysql to communicate with MySQL
- Each connection is a TCP socket to the MySQL server
- Connections are created, used, and returned to the pool
- If all connections are in use, new requests WAIT
"""
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=settings.DATABASE_ECHO,       # Print SQL queries to console
    pool_size=settings.DATABASE_POOL_SIZE,  # Max connections in pool
    pool_recycle=settings.DATABASE_POOL_RECYCLE,  # Recycle after N seconds
    pool_pre_ping=True,                # Verify connection before using
)


# ============================================
# ASYNCHRONOUS ENGINE
# ============================================

"""
The async engine manages a pool of NON-BLOCKING database connections.

Under the hood:
- Uses aiomysql to communicate with MySQL
- Uses Python's asyncio event loop
- When a query is sent, the coroutine YIELDS control
- The event loop handles other requests while waiting
- When MySQL responds, the coroutine RESUMES
"""
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=True,
)


# ============================================
# SESSION FACTORIES
# ============================================

"""
A session factory creates new Session objects.

Think of a factory as a template:
- You configure it ONCE with the engine
- It produces identical Session objects on demand
- Each Session is a unit of work (add, modify, commit, rollback)

Sync factory → produces sync Session objects
Async factory → produces async AsyncSession objects
"""

# Sync session factory
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,     # Don't auto-commit (we control transactions)
    autoflush=False,      # Don't auto-flush (we control when SQL executes)
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Don't expire objects after commit (async needs this)
)


# ============================================
# BASE CLASS FOR MODELS
# ============================================

"""
DeclarativeBase is the parent class for all our ORM models.

When you create a model:
    class Product(Base):
        ...

SQLAlchemy registers it in Base.metadata.
When we call Base.metadata.create_all(), ALL registered models
are created as tables in the database.
"""

class Base(DeclarativeBase):
    """
    Base class for all database models.
    
    All our table classes will inherit from this:
    - Product(Base)
    - User(Base)
    - Cart(Base)
    - Order(Base)
    
    This registers them in Base.metadata for table creation.
    """
    pass


# ============================================
# TABLE CREATION (SYNC)
# ============================================

def create_tables():
    """
    Create all database tables.
    
    This function:
    1. Looks at Base.metadata (registry of all models)
    2. Generates CREATE TABLE statements
    3. Executes them using the SYNC engine
    4. Only creates tables that don't already exist
    
    This is SYNCHRONOUS because SQLAlchemy's create_all is sync.
    We call it once during startup, not during request handling.
    """
    Base.metadata.create_all(bind=sync_engine)


# ============================================
# DEPENDENCY: GET SYNC SESSION
# ============================================

def get_sync_session() -> Generator[Session, None, None]:
    """
    Provide a SYNCHRONOUS database session.
    
    Used for:
    - Scripts that run outside of FastAPI
    - Operations where async isn't needed
    
    Yields:
        Session: A SQLAlchemy Session object
    """
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ============================================
# DEPENDENCY: GET ASYNC SESSION
# ============================================

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an ASYNCHRONOUS database session.
    
    This is the PRIMARY session for FastAPI endpoints.
    Every API request should use this.
    
    Lifecycle:
    1. FastAPI calls get_async_session()
    2. A new AsyncSession is created
    3. The session is yielded to the endpoint
    4. The endpoint uses the session for queries
    5. After the endpoint returns, the session is closed
    
    Yields:
        AsyncSession: A SQLAlchemy AsyncSession object
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()




        