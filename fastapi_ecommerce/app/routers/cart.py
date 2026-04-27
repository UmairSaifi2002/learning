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
async def get_cart():
    """
    View all items in the cart.
    
    Returns:
        Cart object with:
        - items: List of cart items
        - total_items: Total quantity of all items
        - total_amount: Total price of all items
    """
    logger.info("GET /cart")
    
    try:
        cart = CartManager.get_cart()
        logger.info(
            f"Cart has {cart.total_items} items, "
            f"total: ${cart.total_amount:.2f}"
        )
        return cart
    except Exception as e:
        logger.error(f"Error fetching cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cart"
        )

@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(item: CartItemAdd):
    """
    Add a product to the cart.
    
    If the product is already in the cart, the quantity is increased.
    If the product is new, it's added as a new item.
    
    Args:
        item: Contains product_id and quantity (request body)
    
    Returns:
        MessageResponse: Success message with details
    
    Raises:
        400: If product not found or insufficient stock
    """
    logger.info(
        f"POST /cart - product_id={item.product_id}, "
        f"quantity={item.quantity}"
    )
    
    try:
        result_message = CartManager.add_to_cart(item)
        return MessageResponse(message=result_message)
        
    except ValueError as e:
        # Business rule violations (product not found, insufficient stock)
        logger.warning(f"Cart validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        )

@router.delete("/{product_id}", response_model=MessageResponse)
async def remove_from_cart(product_id: int):
    """
    Remove a product from the cart.
    
    Args:
        product_id: ID of the product to remove (path parameter)
    
    Returns:
        MessageResponse: Success confirmation
    
    Raises:
        404: If product is not in the cart
    """
    logger.info(f"DELETE /cart/{product_id}")
    
    try:
        removed = CartManager.remove_from_cart(product_id)
        
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} is not in the cart"
            )
        
        return MessageResponse(
            message=f"Product {product_id} removed from cart"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) as-is
        raise
    except Exception as e:
        logger.error(f"Error removing from cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item from cart"
        )










