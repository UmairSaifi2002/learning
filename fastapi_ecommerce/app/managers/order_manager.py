"""
Order Manager - MySQL Database Version
"""

from typing import List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db_models import Order, OrderItem, Product, CartItem
from app.models.schemas import Order as OrderSchema, OrderItem as OrderItemSchema
from app.utils.loggers import logger


class OrderManager:

    @staticmethod
    async def get_all_orders(
        session: AsyncSession,
        user_id: int
    ) -> List[OrderSchema]:
        """Get all orders for a user."""
        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))  # Eager load order items
        )
        result = await session.execute(query)
        orders = result.scalars().all()
        
        # Convert to Pydantic schema
        return [
            OrderSchema(
                id=order.id,
                items=[
                    OrderItemSchema(
                        product_id=item.product_id,
                        product_name=item.product_name,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        total_price=item.total_price,
                    )
                    for item in order.items
                ],
                total_amount=order.total_amount,
                created_at=order.created_at.isoformat(),
            )
            for order in orders
        ]
    
    @staticmethod
    async def create_order(
        session: AsyncSession,
        user_id: int
    ) -> OrderSchema:
        """Create an order from cart items."""
        logger.info(f"Creating order for user: {user_id}")
    
        # Get cart items with products eagerly loaded
        cart_query = (
            select(CartItem)
            .where(CartItem.user_id == user_id)
            .options(selectinload(CartItem.product))  # ← Eager load product
        )
        result = await session.execute(cart_query)
        cart_items = result.scalars().all()
    
        if not cart_items:
            raise ValueError("Cannot create order with empty cart")
    
        # Validate all items
        for cart_item in cart_items:
            product = cart_item.product
            if not product:
                raise ValueError(f"Product no longer exists")
            if product.stock < cart_item.quantity:
                raise ValueError(
                    f"Insufficient stock for '{product.name}'. "
                    f"Available: {product.stock}"
                )
    
        # Calculate total
        total_amount = sum(
            item.quantity * item.product.price for item in cart_items
        )
    
        # Create order
        order = Order(
            user_id=user_id,
            total_amount=round(total_amount, 2),
        )
        session.add(order)
        await session.flush()  # Get order ID without committing
    
        # Create order items and deduct stock
        # Also build the response items list
        response_items = []
    
        for cart_item in cart_items:
            product = cart_item.product

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                quantity=cart_item.quantity,
                unit_price=product.price,
                total_price=round(cart_item.quantity * product.price, 2),
            )
            session.add(order_item)

            # Build response item (before we lose the data)
            response_items.append(OrderItemSchema(
                product_id=product.id,
                product_name=product.name,
                quantity=cart_item.quantity,
                unit_price=product.price,
                total_price=round(cart_item.quantity * product.price, 2),
            ))

            # Deduct stock
            product.stock -= cart_item.quantity

            # Remove from cart
            await session.delete(cart_item)
    
        # Commit everything
        await session.commit()
    
        # ❌ DO NOT refresh - it will trigger lazy loading error
        # await session.refresh(order)
    
        # ✅ Build response from data we already have
        return OrderSchema(
            id=order.id,
            items=response_items,
            total_amount=order.total_amount,
            created_at=order.created_at.isoformat(),
        )

    # @staticmethod
    # async def create_order(
    #     session: AsyncSession,
    #     user_id: int
    # ) -> OrderSchema:
    #     """Create an order from cart items."""
    #     logger.info(f"Creating order for user: {user_id}")
        
    #     # Get cart items
    #     cart_query = (
    #         select(CartItem)
    #         .where(CartItem.user_id == user_id)
    #         .options(selectinload(CartItem.product))
    #     )
    #     result = await session.execute(cart_query)
    #     cart_items = result.scalars().all()
        
    #     if not cart_items:
    #         raise ValueError("Cannot create order with empty cart")
        
    #     # Validate all items
    #     for cart_item in cart_items:
    #         product = cart_item.product
    #         if not product:
    #             raise ValueError(f"Product no longer exists")
    #         if product.stock < cart_item.quantity:
    #             raise ValueError(
    #                 f"Insufficient stock for '{product.name}'. "
    #                 f"Available: {product.stock}"
    #             )
        
    #     # Create order
    #     total_amount = sum(
    #         item.quantity * item.product.price for item in cart_items
    #     )
        
    #     order = Order(
    #         user_id=user_id,
    #         total_amount=round(total_amount, 2),
    #     )
    #     session.add(order)
    #     await session.flush()  # Get order ID without committing
        
    #     # Create order items and deduct stock
    #     for cart_item in cart_items:
    #         product = cart_item.product
            
    #         order_item = OrderItem(
    #             order_id=order.id,
    #             product_id=product.id,
    #             product_name=product.name,
    #             quantity=cart_item.quantity,
    #             unit_price=product.price,
    #             total_price=round(cart_item.quantity * product.price, 2),
    #         )
    #         session.add(order_item)
            
    #         # Deduct stock
    #         product.stock -= cart_item.quantity
            
    #         # Remove from cart
    #         await session.delete(cart_item)
        
    #     await session.commit()
    #     await session.refresh(order)
        
    #     return OrderSchema(
    #         id=order.id,
    #         items=[
    #             OrderItemSchema(
    #                 product_id=item.product_id,
    #                 product_name=item.product_name,
    #                 quantity=item.quantity,
    #                 unit_price=item.unit_price,
    #                 total_price=item.total_price,
    #             )
    #             for item in order.items
    #         ],
    #         total_amount=order.total_amount,
    #         created_at=order.created_at.isoformat(),
    #     )