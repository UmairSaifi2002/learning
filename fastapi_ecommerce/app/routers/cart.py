"""
Cart Router

Handles HTTP requests for cart endpoints.

Endpoints:
    GET  /cart              - View cart with items and totals
    POST /cart              - Add a product to cart
    DELETE /cart/{product_id} - Remove a product from cart
"""

from fastapi import APIRouter, HTTPException, status

from app.managers.cart_manager import CartManager
from app.models.schemas import Cart, CartItemAdd, MessageResponse
from app.utils.loggers import logger

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)

@router.get("/", response_model=Cart)
async def get_cart(user_id: int = 1):
    """
    View all items in the cart for a specific user.
    
    Args:
        user_id: The user's ID (query parameter). Default is 1.
    
    Example:
        GET /cart?user_id=1
        GET /cart?user_id=2
    """
    logger.info(f"GET /cart - user_id={user_id}")
    
    try:
        cart = CartManager.get_cart(user_id=user_id)
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

@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(item: CartItemAdd, user_id: int = 1):
    """
    Add a product to a specific user's cart.
    
    Args:
        item: Contains product_id and quantity (request body)
        user_id: The user's ID (query parameter). Default is 1.
    
    Example:
        POST /cart?user_id=1
        Body: {"product_id": 1, "quantity": 2}
    """
    logger.info(
        f"POST /cart - user_id={user_id}, "
        f"product_id={item.product_id}, quantity={item.quantity}"
    )
    
    try:
        result_message = CartManager.add_to_cart(item, user_id=user_id)
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
async def remove_from_cart(product_id: int, user_id: int = 1):
    """
    Remove a product from a specific user's cart.
    
    Args:
        product_id: ID of the product to remove (path parameter)
        user_id: The user's ID (query parameter). Default is 1.
    
    Example:
        DELETE /cart/1?user_id=1
    """
    logger.info(f"DELETE /cart/{product_id} - user_id={user_id}")
    
    try:
        removed = CartManager.remove_from_cart(product_id, user_id=user_id)
        
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










