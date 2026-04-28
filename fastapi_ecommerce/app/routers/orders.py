"""
Order Router

Handles HTTP requests for order endpoints.

Endpoints:
    GET  /orders  - View all placed orders
    POST /orders  - Create an order from current cart
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from app.managers.order_manager import OrderManager
from app.models.schemas import Order
from app.utils.loggers import logger

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)

@router.get("/", response_model=List[Order])
async def get_orders(user_id: int = 1):
    """
    View all placed orders for a specific user.
    
    Args:
        user_id: The user's ID (query parameter). Default is 1.
    
    Example:
        GET /orders?user_id=1
        GET /orders?user_id=2
    """
    logger.info(f"GET /orders - user_id={user_id}")
    
    try:
        orders = OrderManager.get_all_orders(user_id=user_id)
        logger.info(f"Returning {len(orders)} orders for user {user_id}")
        return orders
    except Exception as e:
        logger.error(f"Error fetching orders for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders"
        )
    
@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(user_id: int = 1):
    """
    Create an order from a specific user's current cart items.
    
    This endpoint:
    1. Gets the user's cart
    2. Validates all items
    3. Deducts stock from inventory
    4. Creates the order for THIS user
    5. Clears THIS user's cart
    6. Returns the order
    
    Args:
        user_id: The user's ID (query parameter). Default is 1.
    
    Example:
        POST /orders?user_id=1
    """
    logger.info(f"POST /orders - user_id={user_id}")
    
    try:
        order = OrderManager.create_order(user_id=user_id)
        logger.info(
            f"Order created for user {user_id}: "
            f"ID {order.id}, total: ${order.total_amount:.2f}"
        )
        return order
    except ValueError as e:
        logger.warning(f"Order creation failed for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating order for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )






