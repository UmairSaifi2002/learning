"""
FastAPI E-Commerce Application - Main Entry Point

This file:
1. Creates the FastAPI application instance
2. Configures CORS middleware
3. Registers all route modules (products, users, cart, orders)
4. Defines root and health endpoints

To run the server:
    poetry run uvicorn app.main:app --reload
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import our configuration module (runs load_dotenv())
#from app.config import configure_cors

# Import all routers
# Each router file contains related endpoints
from fastapi_ecommerce.app.routers.v1 import users

# Adding middleware for timing requests
from fastapi_ecommerce.app.middleware.v1.timing import add_process_time_header

# Import database session and table creation function
# from app.db.session import create_db_and_tables, engine
# from app.db.database import create_tables, sync_engine, async_engine
from fastapi_ecommerce.app.db.v1.sync import create_tables, sync_engine
from fastapi_ecommerce.app.db.v1.async_db import async_engine

# Import logger for structured logging
from fastapi_ecommerce.app.utils.v1.loggers import logger

# Import settings for application configuration
from fastapi_ecommerce.app.config.v1.settings import settings
from fastapi_ecommerce.app.routers.v1 import cart, orders, products


# ============================================
def configure_cors(app):
    """
    Configure CORS middleware for the FastAPI application.
    
    CORS middleware runs on EVERY request.
    It adds headers that tell browsers:
    "This API accepts requests from these origins."
    
    Args:
        app: FastAPI application instance
    
    How it works:
    1. Browser sends "preflight" OPTIONS request
    2. CORS middleware responds with allowed origins/methods/headers
    3. Browser checks: "Is my origin in the allowed list?"
    4. If yes → Browser sends the actual request
    5. If no → Browser blocks the request (shows CORS error in console)
    """
    
    # Get allowed origins from .env, or use safe defaults
    # If .env has CORS_ORIGINS=*, split gives ["*"]
    # If .env is missing, default to localhost origins
    origins_str = settings.CORS_ORIGINS or "http://localhost:3000,http://localhost:8000"
    origins = [origin.strip() for origin in origins_str.split(",")]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,       # Which domains can call this API
        allow_credentials=True,       # Allow cookies/auth headers
        allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
        allow_headers=["*"],          # Allow all request headers
    )
# ============================================



# ============================================
# LIFESPAN FUNCTION
# ============================================

# ============================================
# LIFESPAN: ENVIRONMENT-AWARE
# ============================================

def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    This function runs code at SERVER STARTUP and SERVER SHUTDOWN.
    The 'yield' keyword separates startup from shutdown.
    
    Behavior changes based on IS_DEVELOPMENT:
    
    DEVELOPMENT (IS_DEVELOPMENT=true):
    - Detailed startup/shutdown logs
    - Database table verification with output
    - Development-specific warnings
    
    PRODUCTION (IS_DEVELOPMENT=false):
    - Minimal startup/shutdown logs
    - Silent database operations
    - No development warnings
    """
    
    # ╔═══════════════════════════════════════════════════════════╗
    # ║                    SERVER STARTUP                          ║
    # ╚═══════════════════════════════════════════════════════════╝
    
    # ============================================
    # DEVELOPMENT: Detailed Startup
    # ============================================
    if settings.IS_DEVELOPMENT:
        logger.info("=" * 60)
        logger.info(f"🚀 STARTING SERVER")
        logger.info(f"📋 Application: {settings.APP_NAME}")
        logger.info(f"📌 Version: {settings.APP_VERSION}")
        logger.info(f"🌍 Environment: {settings.ENVIRONMENT_TYPE}")
        logger.info(f"🔧 Host: {settings.APP_HOST}:{settings.APP_PORT}")
        logger.info(f"📊 Database: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")
        logger.info(f"🗄️  DB Pool Size: {settings.DATABASE_POOL_SIZE}")
        logger.info(f"🔄 SQL Logging: {'ON' if settings.DATABASE_ECHO else 'OFF'}")
        logger.info(f"📝 Log Level: {settings.LOG_LEVEL}")
        logger.info(f"🌐 CORS Origins: {settings.CORS_ORIGINS_LIST}")
        logger.info(f"🐛 Debug Mode: {'ON' if settings.APP_DEBUG else 'OFF'}")
        logger.info("=" * 60)
    else:
        # ============================================
        # PRODUCTION: Minimal Startup
        # ============================================
        logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        logger.info(f"Environment: PRODUCTION")
    
    # ============================================
    # CREATE DATABASE TABLES
    # ============================================
    
    if settings.IS_DEVELOPMENT:
        logger.info("📊 Checking database tables...")
    
    try:
        # create_db_and_tables() # <---- Creating tables here from session.py file
        create_tables() # <---- Creating tables here from database.py file
        
        if settings.IS_DEVELOPMENT:
            logger.info("✅ Database tables ready")
            logger.info("💡 Tip: Visit http://127.0.0.1:8000/docs for API documentation")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {str(e)}")
        if settings.IS_DEVELOPMENT:
            logger.error("💡 Check if MySQL is running and credentials are correct")
            logger.error(f"   Connection: {settings.DATABASE_URL}")
        raise  # Re-raise to prevent server from starting with broken DB
    
    # ============================================
    # DEVELOPMENT-SPECIFIC WARNINGS
    # ============================================
    if settings.IS_DEVELOPMENT:
        # Warn about development-only settings
        if settings.CORS_ORIGINS == "*":
            logger.warning("⚠️  CORS is set to '*' - ALL origins are allowed!")
            logger.warning("   This is fine for development but NOT for production.")
        
        if settings.APP_DEBUG:
            logger.warning("⚠️  Debug mode is ON - error details will be shown to clients.")
            logger.warning("   This is fine for development but NOT for production.")
        
        if not settings.DATABASE_PASSWORD:
            logger.warning("⚠️  Database password is empty! This is a security risk.")
    
    # ╔═══════════════════════════════════════════════════════════╗
    # ║              THE DIVIDING LINE (yield)                    ║
    # ║   Everything ABOVE runs at STARTUP                        ║
    # ║   Everything BELOW runs at SHUTDOWN                       ║
    # ╚═══════════════════════════════════════════════════════════╝
    
    yield
    
    # ╔═══════════════════════════════════════════════════════════╗
    # ║                    SERVER SHUTDOWN                        ║
    # ╚═══════════════════════════════════════════════════════════╝
    
    # ============================================
    # DEVELOPMENT: Detailed Shutdown
    # ============================================
    if settings.IS_DEVELOPMENT:
        logger.info("=" * 60)
        logger.info("🛑 SHUTTING DOWN SERVER")
        logger.info(f"📋 Application: {settings.APP_NAME}")
        logger.info("=" * 60)
    else:
        # PRODUCTION: Minimal Shutdown
        logger.info(f"Stopping {settings.APP_NAME}")
    
    # ============================================
    # CLOSE DATABASE CONNECTIONS
    # ============================================
    
    try:
        sync_engine.dispose() # <---- Dispose sync engine to close all connections in the pool
        # async_engine.dispose() # <---- Dispose async engine as well
        
        if settings.IS_DEVELOPMENT:
            logger.info("📊 Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database connections: {str(e)}")
    
    # ============================================
    # FINAL SHUTDOWN MESSAGE
    # ============================================
    
    if settings.IS_DEVELOPMENT:
        logger.info("✅ Server shutdown complete")
        logger.info("=" * 60)
        logger.info("👋 Goodbye! Server has stopped.")
    else:
        logger.info("Server stopped")




def create_app() -> FastAPI:
    """
    Application factory function.
    
    Creates and configures a FastAPI application instance.
    This pattern is called "Application Factory" - it lets us:
    - Create multiple app instances (useful for testing)
    - Configure the app before returning it
    - Keep the module-level clean
    
    Returns:
        FastAPI: Fully configured application ready to serve requests
    """
    # Create the FastAPI instance with metadata from .env
    # This metadata appears in the auto-generated OpenAPI documentation
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="""
        ## Simple E-Commerce API
        
        Built with FastAPI, Pydantic, and Poetry.
        
        ### Features
        - **Products**: View and manage product catalog
        - **Users**: User management
        - **Cart**: Shopping cart with automatic price calculation
        - **Orders**: Create orders from cart items
        
        ### Technical Details
        - **Storage**: In-memory (lists and dictionaries)
        - **Validation**: Automatic via Pydantic models
        - **Documentation**: Auto-generated at /docs and /redoc
        - **Logging**: Structured logging to console
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,  # Attach the lifespan function for startup/shutdown handling
    )
    
    # Configure CORS middleware
    # This must be done BEFORE routes are registered
    # Middleware wraps all requests including route handling
    # configure_cors(app) # <--- We can call this function to set up CORS based on settings
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS_LIST,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS.split(","),
        allow_headers=settings.CORS_ALLOW_HEADERS.split(","),
    )

    # Add timing middleware
    # @app.middleware() is a DECORATOR that registers middleware
    # The "http" parameter means this is HTTP-level middleware
    app.middleware("http")(add_process_time_header)
    
    # Register all route modules
    # This attaches the endpoints defined in each router file
    # to the main application
    register_routers(app)

    logger.info("✅ Application instance created and configured")
    
    return app


def register_routers(app: FastAPI):
    """
    Register all router modules with the application.
    
    Each router was created with a prefix:
    - products router: prefix="/products"
    - users router: prefix="/users"
    - cart router: prefix="/cart"
    - orders router: prefix="/orders"
    
    So the final URLs become:
    - GET /products
    - GET /users
    - POST /cart
    - POST /orders
    
    Args:
        app: FastAPI application instance
    """
    app.include_router(products.router)
    app.include_router(users.router)
    app.include_router(cart.router)
    app.include_router(orders.router)
    logger.info("📌 Routers registered: products, users, cart, orders")


# ============================================
# CREATE THE APPLICATION INSTANCE
# ============================================
# This is what Uvicorn looks for when we run:
# poetry run uvicorn app.main:app
app = create_app()


# ============================================
# ROOT AND UTILITY ENDPOINTS
# ============================================
# These don't belong to any specific module
# So we define them directly on the app

@app.get("/")
async def root():
    """
    Root endpoint - returns API information and links.
    
    This is the first thing users see when they visit the API.
    """
    return {
        "message": "Welcome to the E-Commerce API",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_spec": "/openapi.json",
        },
        "endpoints": {
            "products": "/products",
            "users": "/users",
            "cart": "/cart",
            "orders": "/orders",
        },
        "version": os.getenv("APP_VERSION", "1.0.0"),
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Used by monitoring tools and load balancers to verify
    the API is running and healthy.
    
    Returns 200 OK if everything is fine.
    """
    return {
        "status": "healthy",
        "service": os.getenv("APP_NAME", "E-Commerce API"),
    }