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