"""
Product Router - API v1

Handles HTTP requests for product endpoints.
Part of the E-Commerce API v1.

Endpoints:
    GET    /api/v1/cart/{id}
    POST   /api/v1/cart/{id}
    DELETE /api/v1/cart/{id}
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.v1 import get_async_session, get_async_session_with_commit
from app.managers.v1.cart_manager import CartManager
from app.models.v1.schemas import Cart, CartItemAdd, MessageResponse
from app.utils.v1.loggers import logger
from app.config.v1.settings import settings

# router = APIRouter(
#     prefix="/api/v1/cart",
#     tags=["Cart"],
# )

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/cart",
    tags=["Cart"],
)


@router.get("/", response_model=Cart)
async def get_cart(
    user_id: int = 1,
    session: AsyncSession = Depends(get_async_session)  # ← ASYNC SESSION
):
    """
    View all items in the cart for a specific user.
    
    Args:
        user_id: The user's ID (query parameter). Default is 1.
        session: Database session (injected automatically)
    
    Example:
        GET /cart?user_id=1
        GET /cart?user_id=2
    """
    logger.info(f"GET /cart - user_id={user_id}")
    
    try:
        # ✅ AWAIT the async manager method
        # ✅ Pass session as first argument
        cart = await CartManager.get_cart(session=session, user_id=user_id)
        logger.info(
            f"Cart for user {user_id}: "
            f"{cart.total_items} items, total: ${cart.total_amount:.2f}"
        )
        return cart
    except Exception as e:
        logger.error(f"Error fetching cart for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cart"
        )


@router.post(
    "/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_to_cart(
    item: CartItemAdd,
    user_id: int = 1,
    session: AsyncSession = Depends(get_async_session_with_commit)  # ← WITH COMMIT
):
    """
    Add a product to a specific user's cart.
    
    Args:
        item: Contains product_id and quantity (request body)
        user_id: The user's ID (query parameter). Default is 1.
        session: Database session (injected automatically)
    
    Example:
        POST /cart?user_id=1
        Body: {"product_id": 1, "quantity": 2}
    """
    logger.info(
        f"POST /cart - user_id={user_id}, "
        f"product_id={item.product_id}, quantity={item.quantity}"
    )
    
    try:
        # ✅ AWAIT the async manager method
        # ✅ Pass session AND item_data AND user_id
        result_message = await CartManager.add_to_cart(
            session=session,
            item_data=item,
            user_id=user_id
        )
        return MessageResponse(message=result_message)
    except ValueError as e:
        logger.warning(f"Cart validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding to cart for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        )


@router.delete("/{product_id}", response_model=MessageResponse)
async def remove_from_cart(
    product_id: int,
    user_id: int = 1,
    session: AsyncSession = Depends(get_async_session_with_commit)  # ← WITH COMMIT
):
    """
    Remove a product from a specific user's cart.
    
    Args:
        product_id: ID of the product to remove (path parameter)
        user_id: The user's ID (query parameter). Default is 1.
        session: Database session (injected automatically)
    
    Example:
        DELETE /cart/1?user_id=1
    """
    logger.info(f"DELETE /cart/{product_id} - user_id={user_id}")
    
    try:
        # ✅ AWAIT the async manager method
        # ✅ Pass session, product_id, and user_id
        removed = await CartManager.remove_from_cart(
            session=session,
            product_id=product_id,
            user_id=user_id
        )
        
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} is not in the cart for user {user_id}"
            )
        
        return MessageResponse(
            message=f"Product {product_id} removed from cart"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from cart for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item from cart"
        )