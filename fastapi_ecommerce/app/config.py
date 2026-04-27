"""
Application Configuration

This module handles:
1. Loading environment variables from .env
2. Configuring CORS (Cross-Origin Resource Sharing)

CORS is needed when your frontend (e.g., React on localhost:3000)
needs to call your API (FastAPI on localhost:8000).
"""

import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load .env file when this module is imported
# This makes all variables in .env available via os.getenv()
load_dotenv()


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
    origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
    origins = [origin.strip() for origin in origins_str.split(",")]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,       # Which domains can call this API
        allow_credentials=True,       # Allow cookies/auth headers
        allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
        allow_headers=["*"],          # Allow all request headers
    )