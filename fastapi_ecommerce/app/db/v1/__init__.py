"""
Database Package

Re-exports everything from sync and async modules
so other parts of the app can import from app.db directly.
"""

from app.db.v1.base import Base

from app.db.v1.sync import (
    sync_engine,
    SyncSessionLocal,
    create_tables,
    drop_table,
    get_sync_session,
)

from app.db.v1.async_db import (
    async_engine,
    AsyncSessionLocal,
    get_async_session,
    get_async_session_with_commit,
)

# ==============================================================================================
"""
Shared Database Base

This module contains ONLY the DeclarativeBase class.
It's separated from sync/async engines to avoid circular imports.

All ORM models inherit from this Base class.
Base.metadata is the registry where all tables are collected.
"""


from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for ALL database models.
    
    Every table class inherits from this:
    
        from app.db.base import Base
        
        class Product(Base):
            __tablename__ = "products"
            id: Mapped[int] = mapped_column(primary_key=True)
            ...
    
    What DeclarativeBase provides:
    - Base.metadata: Registry of all tables
    - Base.metadata.create_all(): Creates all tables
    - Base.metadata.drop_all(): Drops all tables
    - Automatic __tablename__ generation
    - Relationship support
    """
    pass


# ==============================================================================================


__all__ = [
    # Base
    "Base",
    # Sync
    "sync_engine",
    "SyncSessionLocal",
    "create_tables",
    "drop_table",
    "get_sync_session",
    # Async
    "async_engine",
    "AsyncSessionLocal",
    "get_async_session",
    "get_async_session_with_commit",
]