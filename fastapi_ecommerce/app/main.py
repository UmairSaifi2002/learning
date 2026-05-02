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

# Import our configuration module (runs load_dotenv())
from app.config import configure_cors

# Import all routers
# Each router file contains related endpoints
from app.routers import products, users, cart, orders

# Adding middleware for timing requests
from app.middleware.timing import add_process_time_header

# Import database session and table creation function
from app.db.session import create_db_and_tables, engine

# Import logger for structured logging
from app.utils.loggers import logger


# ============================================
# LIFESPAN FUNCTION
# ============================================

def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    This function manages what happens when the server STARTS and STOPS.
    
    STARTUP (before yield):
    - Called automatically when you run: poetry run uvicorn app.main:app
    - Creates database tables if they don't exist
    - Logs the startup information
    
    SHUTDOWN (after yield):
    - Called automatically when you press CTRL+C
    - Closes database connections
    - Logs the shutdown information
    
    HOW IT WORKS:
    FastAPI treats this function as a GENERATOR.
    - It calls next() once → runs code until yield → STARTUP complete
    - Server runs and handles requests
    - When stopping, it calls next() again → runs code after yield → SHUTDOWN
    
    Args:
        app: The FastAPI application instance (passed automatically by FastAPI)
    """
    # ╔═══════════════════════════════════════════════════════════╗
    # ║                    SERVER STARTUP                          ║
    # ╚═══════════════════════════════════════════════════════════╝
    
    logger.info("=" * 60)
    logger.info(f"🚀 STARTING SERVER: {os.getenv('APP_NAME', 'E-Commerce API')}")
    logger.info(f"📋 Version: {os.getenv('APP_VERSION', '1.0.0')}")
    logger.info("=" * 60)
    
    # Create all database tables
    # This ensures the tables exist before any request arrives
    # If tables already exist, this does nothing (safe to run multiple times)
    logger.info("📊 Checking database tables...")
    create_db_and_tables()
    logger.info("✅ Database tables ready")
    
    # The YIELD marks the end of STARTUP and the beginning of SHUTDOWN
    # Everything above this line runs at startup
    # Everything below this line runs at shutdown

    # Print to console directly too (backup)
    print("✅ STARTUP COMPLETE: Server is ready")

    yield
    
    # ╔═══════════════════════════════════════════════════════════╗
    # ║                    SERVER SHUTDOWN                         ║
    # ╚═══════════════════════════════════════════════════════════╝
    
    logger.info("=" * 60)
    logger.info("🛑 SHUTTING DOWN SERVER...")
    
    # Close all database connections
    # engine.dispose() closes the connection pool
    # This ensures no connections are left hanging
    engine.dispose()
    logger.info("📊 Database connections closed")
    
    logger.info("✅ Server shutdown complete")
    logger.info("=" * 60)

    print("✅ SHUTDOWN COMPLETE")



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
        title=os.getenv("APP_NAME", "E-Commerce API"),
        version=os.getenv("APP_VERSION", "1.0.0"),
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
    configure_cors(app)

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