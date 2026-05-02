"""
Database Session Module

Handles MySQL database connection, table creation, and session management.
Uses SQLModel (built on SQLAlchemy) for ORM operations.

This module provides:
1. engine - The database engine that manages connections
2. create_db_and_tables() - Creates all tables on startup
3. get_session() - Provides a session per request
4. SessionDep - Shortcut type for dependency injection
"""

import os
from typing import Annotated, Generator
from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

# Load .env
load_dotenv()

# ============================================
# ENVIRONMENT CHECK
# ============================================

IS_DEVELOPMENT = os.getenv("IS_DEVELOPMENT", "false").lower() == "true"

# ============================================
# DATABASE CONFIGURATION
# ============================================

DB_USER = os.getenv("DATABASE_USER", "root")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "3306")
DB_NAME = os.getenv("DATABASE_NAME", "ecommerce_db")

MYSQL_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

"""
The connection URL tells SQLModel where to find the database.

Format: mysql+pymysql://USER:PASSWORD@HOST:PORT/DATABASE_NAME

IMPORTANT: 
- Replace 'your_password' with your actual MySQL password
- The database 'ecommerce_db' must exist, or MySQL must be configured
  to create it automatically
"""



# ============================================
# CREATE THE ENGINE
# ============================================

"""
The engine is the heart of database communication.
It manages a POOL of connections for efficiency.

Instead of opening/closing a new connection for every request,
the engine keeps several connections open and ready to use.
This is much faster.

Parameters:
- echo=True: Print every SQL query to the console (GREAT FOR LEARNING!)
  Set to False in production
- pool_size: Number of connections to keep open (default 5)
"""
engine = create_engine(
    MYSQL_URL,
    echo=True,       # Logs all SQL queries to console
    pool_size=10,    # Keep 10 connections ready in the pool
)

# ============================================
# TABLE CREATION FUNCTION
# ============================================

def create_db_and_tables():
    """
    Create all database tables defined in our models.
    
    How it works:
    1. SQLModel keeps a 'metadata' registry of all classes with table=True
    2. When we import our model files, they register themselves
    3. metadata.create_all(engine) generates CREATE TABLE SQL for all of them
    4. It only creates tables that DON'T already exist (safe to run multiple times)
    
    This function should be called ONCE during application startup.
    """
    from app.models import db_models  # ← This triggers registration
    SQLModel.metadata.create_all(engine)

# ============================================
# SESSION FACTORY (PER-REQUEST SESSION)
# ============================================

def get_session():
    """
    Create a NEW database session for each API request.
    
    This is a GENERATOR function (uses 'yield' instead of 'return').
    
    HOW YIELD WORKS HERE:
    1. FastAPI calls get_session()
    2. A new Session is created
    3. The session is 'yield'-ed to the endpoint function
    4. The endpoint uses the session (queries, inserts, updates)
    5. After the endpoint finishes, code AFTER yield runs
    6. The session is automatically closed
    
    This ensures:
    - Each request has its own isolated session
    - Sessions are always closed (even if errors occur)
    - Connections return to the pool for reuse
    """
    with Session(engine) as session:
        yield session
    # Session is automatically closed here
    # Even if an exception occurs, the 'with' block handles cleanup

# ============================================
# SESSION DEPENDENCY TYPE
# ============================================

"""
SessionDep is a TYPE ALIAS that combines:
- The type: Session
- The dependency: Depends(get_session)

Now instead of writing:
    def my_endpoint(session: Session = Depends(get_session)):
        ...

We can write:
    def my_endpoint(session: SessionDep):
        ...

This is cleaner, shorter, and prevents typos.
"""
SessionDep = Annotated[Session, Depends(get_session)]