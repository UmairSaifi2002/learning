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



