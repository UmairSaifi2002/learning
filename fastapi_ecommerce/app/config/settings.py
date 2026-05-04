"""
Application Settings Module

Centralized configuration using Pydantic BaseSettings.
All environment variables are loaded, validated, and accessible
through a single 'settings' instance.

Usage:
    from app.config.settings import settings
    print(settings.APP_NAME)
    print(settings.DATABASE_URL)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Centralized application settings.
    
    Each class attribute:
    1. Has a type annotation (validated automatically)
    2. Has a default value (used if env variable is missing)
    3. Can be overridden by .env file or system environment
    
    Configuration is loaded in this priority (highest to lowest):
    1. Constructor arguments: Settings(APP_PORT=9000)
    2. System environment variables
    3. .env file
    4. Default values in class definition
    """
    
    # ============================================
    # ENVIRONMENT
    # ============================================
    
    IS_DEVELOPMENT: bool = True
    """
    Controls whether the app runs in development or production mode.
    
    Development (True):
    - SQL queries are logged to console
    - Debug-level logging is enabled
    - CORS allows all origins
    
    Production (False):
    - SQL queries are hidden
    - Only warnings and errors are logged
    - CORS is restricted to specific origins
    """
    
    # ============================================
    # APPLICATION
    # ============================================
    
    APP_NAME: str = "E-Commerce API"
    """The name displayed in API documentation and logs."""
    
    APP_VERSION: str = "1.0.0"
    """Current application version."""
    
    APP_HOST: str = "127.0.0.1"
    """Host address to bind the server to."""
    
    APP_PORT: int = 8000
    """Port number for the server."""
    
    APP_DEBUG: bool = True
    """Enable debug mode (detailed error pages)."""
    
    # ============================================
    # DATABASE
    # ============================================
    
    DATABASE_USER: str = "root"
    """MySQL database username."""
    
    DATABASE_PASSWORD: str = "umair"
    """MySQL database password."""
    
    DATABASE_HOST: str = "localhost"
    """MySQL database host address."""
    
    DATABASE_PORT: int = 3306
    """MySQL database port number."""
    
    DATABASE_NAME: str = "MYSQL Ecommerce_DB"
    """MySQL database name."""
    
    DATABASE_POOL_SIZE: int = 10
    """Number of database connections to keep in the pool."""
    
    DATABASE_POOL_RECYCLE: int = 3600
    """Seconds before a connection is recycled (prevents stale connections)."""
    
    DATABASE_ECHO: bool = True
    """If True, SQL queries are printed to console."""
    
    # ============================================
    # CORS
    # ============================================
    
    CORS_ORIGINS: str = "*"
    """
    Allowed CORS origins.
    Comma-separated list of domains, or '*' for all origins.
    
    Development: "*"
    Production: "https://yourdomain.com,https://app.yourdomain.com"
    """
    
    CORS_ALLOW_CREDENTIALS: bool = True
    """Allow cookies and authentication headers in cross-origin requests."""
    
    CORS_ALLOW_METHODS: str = "*"
    """HTTP methods allowed for cross-origin requests."""
    
    CORS_ALLOW_HEADERS: str = "*"
    """HTTP headers allowed for cross-origin requests."""
    
    # ============================================
    # LOGGING
    # ============================================
    
    LOG_LEVEL: str = "DEBUG"
    """
    Logging level.
    
    Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    Development: DEBUG (shows everything)
    Production: WARNING (shows important only)
    """
    
    LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    """Format string for log messages."""
    
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    """Date format for log timestamps."""
    
    # ============================================
    # PYDANTIC CONFIGURATION
    # ============================================
    
    model_config = SettingsConfigDict(
        # Location of .env file
        env_file=".env",
        
        # Encoding of .env file
        env_file_encoding="utf-8",
        
        # If True, extra attributes from .env are ignored (not errors)
        extra="ignore",
        
        # Case sensitivity for environment variable names
        # False means APP_NAME and app_name both work
        case_sensitive=False,
    )
    
    # ============================================
    # COMPUTED PROPERTIES
    # ============================================
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Construct the MySQL connection URL from individual settings.
        
        This is a COMPUTED PROPERTY - it's not stored, it's calculated.
        Every time you access settings.DATABASE_URL, it builds the URL.
        
        Returns:
            str: MySQL connection URL
        """
        return (
            f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
    
    @property
    def IS_PRODUCTION(self) -> bool:
        """Convenience property: True if NOT in development mode."""
        return not self.IS_DEVELOPMENT
    
    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        """
        Parse CORS_ORIGINS string into a list.
        
        Converts "http://a.com,http://b.com" → ["http://a.com", "http://b.com"]
        Converts "*" → ["*"]
        """
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
        ]
    
    @property
    def ENVIRONMENT_TYPE(self) -> str:
        """Human-readable environment type."""
        return "DEVELOPMENT" if self.IS_DEVELOPMENT else "PRODUCTION"


# ============================================
# GLOBAL SETTINGS INSTANCE
# ============================================

# Create a single instance that can be imported anywhere
# This loads .env and validates all settings ONE TIME
settings = Settings()

# Print settings summary on first import (helpful for debugging)
print(f"✅ Settings loaded: {settings.APP_NAME} v{settings.APP_VERSION}")
print(f"🌍 Environment: {settings.ENVIRONMENT_TYPE}")
print(f"📊 Database: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")
print(f"🔄 SQL Logging: {'ON' if settings.DATABASE_ECHO else 'OFF'}")