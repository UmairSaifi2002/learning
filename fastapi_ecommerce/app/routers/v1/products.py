"""
Product Router - MySQL Database Version

All endpoints now use async database sessions.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_ecommerce.app.db.v1 import get_async_session, get_async_session_with_commit
from fastapi_ecommerce.app.managers.v1.product_manager import ProductManager
from fastapi_ecommerce.app.models.v1.schemas import ProductCreate, ProductUpdate, Product, MessageResponse
from fastapi_ecommerce.app.utils.v1.loggers import logger

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=List[Product])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session)  # ← ASYNC SESSION
):
    """Get all products with pagination."""
    logger.info(f"GET /products - skip={skip}, limit={limit}")
    try:
        products = await ProductManager.get_all_products(
            session=session, skip=skip, limit=limit
        )
        return products
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch products"
        )


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_async_session)  # ← ASYNC SESSION
):
    """Get a single product by ID."""
    logger.info(f"GET /products/{product_id}")
    
    product = await ProductManager.get_product(
        session=session, product_id=product_id
    )
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    return product


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED
)
async def create_product(
    product_data: ProductCreate,
    session: AsyncSession = Depends(get_async_session_with_commit)  # ← WITH COMMIT
):
    """Create a new product."""
    logger.info(f"POST /products - Creating: {product_data.name}")
    
    try:
        new_product = await ProductManager.create_product(
            session=session, product_data=product_data
        )
        return new_product
    except Exception as e:
        logger.error(f"Failed to create product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    session: AsyncSession = Depends(get_async_session_with_commit)  # ← WITH COMMIT
):
    """Update an existing product."""
    logger.info(f"PUT /products/{product_id}")
    
    updated_product = await ProductManager.update_product(
        session=session, product_id=product_id, product_data=product_data
    )
    
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    return updated_product


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_async_session_with_commit)  # ← WITH COMMIT
):
    """Delete a product."""
    logger.info(f"DELETE /products/{product_id}")
    
    deleted = await ProductManager.delete_product(
        session=session, product_id=product_id
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    return MessageResponse(
        message=f"Product {product_id} deleted successfully"
    )