"""
Database Package

Re-exports everything from sync and async modules
so other parts of the app can import from app.db directly.
"""

from fastapi_ecommerce.app.db.v1.base import Base

from fastapi_ecommerce.app.db.v1.sync import (
    sync_engine,
    SyncSessionLocal,
    create_tables,
    drop_table,
    get_sync_session,
)

from fastapi_ecommerce.app.db.v1.async_db import (
    async_engine,
    AsyncSessionLocal,
    get_async_session,
    get_async_session_with_commit,
)

__all__ = [
    # Base
    "Base",
    # Sync
    "sync_engine",
    "SyncSessionLocal",
    "create_tables",
    "drop_tables",
    "get_sync_session",
    # Async
    "async_engine",
    "AsyncSessionLocal",
    "get_async_session",
    "get_async_session_with_commit",
]