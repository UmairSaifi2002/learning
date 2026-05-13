"""
Synchronous Database Module

This module handles ALL synchronous database operations:
- Creating the sync engine (pymysql driver)
- Creating the sync session factory
- Providing sync sessions (for scripts, table creation)
- Creating all database tables

Use this module when:
- You need to create tables (Base.metadata.create_all is SYNC)
- You're writing scripts or management commands
- You're running code outside of FastAPI's async context

DO NOT use sync sessions inside FastAPI endpoints.
Use async sessions (from async_db.py) for API requests.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config.v1.settings import settings
from app.db.v1 import Base
from app.utils.v1.loggers import logger

# ============================================
# SYNCHRONOUS DATABASE URL
# ============================================

"""
The sync URL uses the 'pymysql' driver.
Format: mysql+pymysql://user:password@host:port/database

pymysql is a PURE PYTHON MySQL driver.
It's synchronous (blocking) - each query freezes the thread until complete.

Why pymysql and not mysql-connector-python?
- pymysql is lighter weight
- pymysql is more widely tested with SQLAlchemy
- pymysql handles connection pooling better
"""

SYNC_DATABASE_URL = (
    f"mysql+pymysql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
)

# ============================================
# SYNCHRONOUS ENGINE & SESSION
# ============================================

"""
The sync engine manages a POOL of blocking database connections.

Under the hood:
┌─────────────────────────────────────────────────────────┐
│                    SYNC ENGINE                          │
│                                                         │
│  Connection Pool (pool_size=10)                         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐           │
│  │Conn 1│ │Conn 2│ │Conn 3│ │Conn 4│ │ ...  │           │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘           │
│     │        │        │        │        │               │
│     │   Each connection is a TCP socket to MySQL        │
│     │   When a connection is in use, others WAIT        │
│     │                                                   │
│     └────────────┬──────────────┘                       │
│                  ▼                                      │
│            MySQL Server                                 │
└─────────────────────────────────────────────────────────┘

Parameters:
- echo: Print SQL to console (from settings.DATABASE_ECHO)
- pool_size: Max simultaneous connections
- pool_recycle: Recycle connections after N seconds
- pool_pre_ping: Test connection before using it
"""

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo = settings.DATABASE_ECHO,
    pool_size = settings.DATABASE_POOL_SIZE,
    pool_recycle = settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping = True
)

# ============================================
# SYNCHRONOUS SESSION FACTORY
# ============================================

"""
SessionLocal is a FACTORY that creates Session objects.

Think of it like a car factory:
- You configure it ONCE (which engine, autocommit settings)
- Every time you call it: SyncSessionLocal() → New Session
- Each Session is independent (separate transaction)

Parameters:
- bind: Which engine to use
- autocommit=False: We control commits manually
- autoflush=False: We control when SQL executes
"""


SyncSessionLocal = sessionmaker(
    bind = sync_engine,
    autocommit = False,
    autoflush = False
)

# ============================================
# Table Creation (SYNC)
# ============================================

def create_tables():
    """
    Create ALL database tables defined in our models.
    
    This function:
    1. Imports all model classes (they register with Base.metadata)
    2. Tells SQLAlchemy to generate CREATE TABLE statements
    3. Executes them against the database
    
    Why is this SYNC?
    - SQLAlchemy's metadata.create_all() is inherently synchronous
    - Creating tables is a one-time startup operation
    - There's no benefit to making it async (no I/O waiting during DDL)
    
    How it works:
    1. Base.metadata contains all registered tables
    2. create_all(bind=sync_engine) iterates through metadata
    3. For each table not existing: generates CREATE TABLE SQL
    4. Executes the SQL using the sync engine
    
    This is SAFE to call multiple times:
    - Tables that already exist are SKIPPED
    - No data is lost
    """
    # Import models here to ensure they're registered in Base.metadata
    # If imported at the top, might cause circular imports
    # Importing here guarantees models are loaded before create_all runs
    from app.models.v1 import db_models

    logger.info("📊 Creating database tables (if they don't exist)...")
    Base.metadata.create_all(bind = sync_engine)
    logger.info("✅ Database tables ready")


def drop_table():
    """
    Drop ALL database tables.
    
    WARNING: This DELETES ALL DATA!
    Only use in development or testing.
    
    This is the opposite of create_tables():
    - DROP TABLE statements are generated
    - All tables are removed from the database
    """

    from fastapi_ecommerce.app.models.v1 import db_models
    logger.warning("⚠️  Dropping all database tables!")
    Base.metadata.drop_all(bind=sync_engine)
    logger.warning("❌ All tables dropped")


# ============================================
# DEPENDENCY: GET SYNC SESSION
# ============================================

def get_sync_session() -> Generator[Session, None, None]:
    """
    Provide a SYNCHRONOUS database session.
    
    Use this for:
    - Management scripts
    - Database seeding
    - Operations outside of FastAPI request handling
    
    Lifecycle:
    1. session = SyncSessionLocal()  ← Get connection from pool
    2. yield session                  ← Give to caller
    3. session.close()               ← Return connection to pool
    
    NEVER use this inside async FastAPI endpoints!
    It will BLOCK the event loop and slow down all requests.
    
    Yields:
        Session: A SQLAlchemy Session object
    """
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        # Always close the session, even if an error occurred
        # This returns the connection to the pool
        session.close()








