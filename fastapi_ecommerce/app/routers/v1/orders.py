"""
Order Router - MySQL Database Version

Handles HTTP requests for order endpoints.
All endpoints use async database sessions.

Endpoints:
    GET  /orders  - View all placed orders
    POST /orders  - Create an order from current cart
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_ecommerce.app.db.v1 import get_async_session, get_async_session_with_commit
from fastapi_ecommerce.app.managers.v1.order_manager import OrderManager
from fastapi_ecommerce.app.models.v1.schemas import Order
from fastapi_ecommerce.app.utils.v1.loggers import logger

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.get("/", response_model=List[Order])
async def get_orders(
    user_id: int = 1,
    session: AsyncSession = Depends(get_async_session)  # ← ASYNC SESSION
):
    """
    View all placed orders for a specific user.
    
    Args:
        user_id: The user's ID (query parameter). Default is 1.
        session: Database session (injected automatically)
    
    Example:
        GET /orders?user_id=1
        GET /orders?user_id=2
    """
    logger.info(f"GET /orders - user_id={user_id}")
    
    try:
        # ✅ AWAIT the async manager method
        # ✅ Pass session and user_id
        orders = await OrderManager.get_all_orders(
            session=session,
            user_id=user_id
        )
        logger.info(f"Returning {len(orders)} orders for user {user_id}")
        return orders
    except Exception as e:
        logger.error(f"Error fetching orders for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders"
        )


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    user_id: int = 1,
    session: AsyncSession = Depends(get_async_session_with_commit)  # ← WITH COMMIT
):
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
        session: Database session (injected automatically)
    
    Example:
        POST /orders?user_id=1
    """
    logger.info(f"POST /orders - user_id={user_id}")
    
    try:
        # ✅ AWAIT the async manager method
        # ✅ Pass session and user_id
        order = await OrderManager.create_order(
            session=session,
            user_id=user_id
        )
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