"""
Database Models (SQLModel ORM)

These classes define the structure of our MySQL tables.
Each class with 'table=True' becomes a real database table.

When the server starts, SQLModel.metadata.create_all(engine)
reads these classes and generates CREATE TABLE statements.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


# ============================================
# PRODUCT TABLE
# ============================================

class Product(SQLModel, table=True):
    """
    Product database table.
    
    This Python class automatically creates a MySQL table named 'product'
    with the following columns:
    
    MySQL Table Structure:
    ┌─────────────┬──────────────┬─────────────────────────┐
    │   Column    │    Type      │      Description        │
    ├─────────────┼──────────────┼─────────────────────────┤
    │ id          │ INT (PK)     │ Auto-incrementing ID    │
    │ name        │ VARCHAR(100) │ Product name (indexed)  │
    │ price       │ FLOAT        │ Product price           │
    │ category    │ VARCHAR(50)  │ Product category        │
    │ stock       │ INT          │ Available quantity      │
    │ created_at  │ DATETIME     │ When product was added  │
    └─────────────┴──────────────┴─────────────────────────┘
    """
    
    # This sets the MySQL table name
    # If you don't set this, the table name defaults to 'product' (lowercase class name)
    __tablename__ = "products"
    
    # ============================================
    # COLUMN DEFINITIONS
    # ============================================
    
    # PRIMARY KEY
    # - Optional[int]: Can be None when creating (database assigns the ID)
    # - primary_key=True: This is the unique identifier
    # - default=None: If no ID is provided, database auto-generates one
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # PRODUCT NAME
    # - str: Must be a string
    # - max_length=100: Maximum 100 characters (becomes VARCHAR(100))
    # - index=True: Creates a database index for faster searches by name
    name: str = Field(max_length=100, index=True)
    
    # PRODUCT PRICE
    # - float: Must be a decimal number
    # - gt=0: Must be greater than 0 (cannot be negative or zero)
    price: float = Field(gt=0)
    
    # PRODUCT CATEGORY
    # - str: Category name
    # - max_length=50: Maximum 50 characters
    # - index=True: Indexed for filtering products by category
    category: str = Field(max_length=50, index=True)
    
    # STOCK QUANTITY
    # - int: Integer value
    # - default=0: If not provided, defaults to 0
    # - ge=0: Must be greater than or equal to 0 (cannot be negative)
    stock: int = Field(default=0, ge=0)
    
    # CREATED TIMESTAMP
    # - datetime: Date and time
    # - default_factory=datetime.now: Sets to current time when record is created
    #   (Using default_factory instead of default ensures each record gets its own timestamp)
    created_at: datetime = Field(default_factory=datetime.now)