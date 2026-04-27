"""
Product Router

Handles HTTP requests for product endpoints.
This is the "presentation layer" - it speaks HTTP.
All business logic is delegated to ProductManager.

Endpoints:
    GET    /products              - List all products (with pagination)
    GET    /products/{id}         - Get a single product
    POST   /products              - Create a new product
    PUT    /products/{id}         - Update an existing product
    DELETE /products/{id}         - Delete a product
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict

# Our Business Logic Layer for products
from app.managers.product_manager import ProductManager

# Our Data Models for request validation and response formatting
from app.models.schemas import ProductCreate, ProductUpdate, Product, MessageResponse

# Our logger for tracking what's happening
from app.utils.loggers import logger


# Create an APIRouter instance
# This is like a mini-FastAPI app just for products
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# What does prefix do?

# Instead of:
# @router.get("/products")
# @router.get("/products/{id}")
# @router.post("/products")

# We write:
# @router.get("/")      # → /products/
# @router.get("/{id}")  # → /products/{id}
# @router.post("/")     # → /products/

@router.get("/", response_model=List[Product])
async def get_products(skip: int=0, limit: int=100) -> List[Product]:
    """
    Get a list of products with optional pagination.

    Query Parameters:
        skip: Number of products to skip (for pagination)
        limit: Maximum number of products to return

    Returns:
        List[Product]: A list of products
    """
    logger.info(f"GET /products - skip={skip}, limit={limit}")
    try:
        products = ProductManager.get_all_products(skip=skip, limit=limit)
        logger.info(f"Returning {len(products)} Products")
        return products
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int) -> Product:
    logger.info(f"GET /products/{product_id}")
    product = ProductManager.get_product(product_id)
    if not product:
        logger.warning(f"Product with ID {product_id} not found")
        raise HTTPException(status_code=404, detail=f"Product with ID: {product_id} not found")
    return product

@router.post("/", response_model=Product, status_code=201)
async def create_product(product_data: ProductCreate):
    logger.info(f"POST /product - data: {product_data}")
    try:
        new_product = ProductManager.create_product(product_data=product_data)
        return new_product
    except Exception as e:
        logger.error(f"Failed to create product: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create product")

@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: int, product_data: ProductUpdate):
    logger.info(f"PUT /products/{product_id} - data: {product_data}")
    updated_product = ProductManager.update_product(product_id, product_data)
    if not updated_product:
        logger.warning(f"Product with ID {product_id} not found for update")
        raise HTTPException(status_code=404, detail=f"Product with ID: {product_id} not found")
    return updated_product

@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(product_id: int):
    logger.info(f"DELETE /products/{product_id}")
    success = ProductManager.delete_product(product_id)
    if not success:
        logger.warning(f"Product with ID {product_id} not found for deletion")
        raise HTTPException(status_code=404, detail=f"Product with ID: {product_id} not found")
    return MessageResponse("message", f"Product with ID: {product_id} deleted successfully")


