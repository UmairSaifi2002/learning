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
async def get_orders():
    """
    View all placed orders.
    
    Returns:
        List[Order]: All orders with their items and totals
    """
    logger.info("GET /orders")
    
    try:
        orders = OrderManager.get_all_orders()
        logger.info(f"Returning {len(orders)} orders")
        return orders
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders"
        )
    
@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order():
    """
    Create an order using current cart items.
    
    This endpoint:
    1. Get the current cart
    2. Validate all items
    3. Deduct stock from inventory
    4. Create the order record
    5. Clear the cart
    6. Return the completed order
    
    Returns:
        Order: The completed order with ID, items, and timestamp
    
    Raises:
        400: If cart is empty, product missing, or insufficient stock
    """
    logger.info("POST /orders")
    
    try:
        order = OrderManager.create_order()
        logger.info(
            f"Order created: ID {order.id}, "
            f"total: ${order.total_amount:.2f}"
        )
        return order
        
    except ValueError as e:
        # Business rule violations (empty cart, missing product, no stock)
        logger.warning(f"Order creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )






