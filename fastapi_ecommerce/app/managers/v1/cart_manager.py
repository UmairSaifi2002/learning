"""
Cart Manager - MySQL Database Version
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fastapi_ecommerce.app.models.v1.db_models import CartItem, Product, User
from fastapi_ecommerce.app.models.v1.schemas import CartItemAdd, Cart, CartItem as CartItemSchema
from fastapi_ecommerce.app.utils.v1.loggers import logger


class CartManager:

    @staticmethod
    async def get_cart(
        session: AsyncSession,
        user_id: int
    ) -> Cart:
        """
        Get user's cart with calculated totals.
        """
        logger.info(f"Getting cart for user: {user_id}")
        
        # Query cart items for this user with product details loaded
        query = (
            select(CartItem)
            .where(CartItem.user_id == user_id)
            .options(selectinload(CartItem.product))  # Eager load product
        )
        result = await session.execute(query)
        cart_items = result.scalars().all()
        
        # Convert ORM objects to Pydantic schema objects
        items = []
        for item in cart_items:
            items.append(CartItemSchema(
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=item.product.price,
                total_price=round(item.quantity * item.product.price, 2)
            ))
        
        total_items = sum(item.quantity for item in items)
        total_amount = sum(item.total_price for item in items)
        
        return Cart(
            items=items,
            total_items=total_items,
            total_amount=round(total_amount, 2)
        )

    @staticmethod
    async def add_to_cart(
        session: AsyncSession,
        item_data: CartItemAdd,
        user_id: int
    ) -> str:
        """Add a product to cart."""
        logger.info(f"Adding to cart: user={user_id}, product={item_data.product_id}")
        
        # Validate product exists
        product = await session.get(Product, item_data.product_id)
        if not product:
            raise ValueError(f"Product {item_data.product_id} not found")
        
        # Validate stock
        if product.stock < item_data.quantity:
            raise ValueError(
                f"Insufficient stock. Available: {product.stock}"
            )
        
        # Check if already in cart
        query = select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == item_data.product_id
        )
        result = await session.execute(query)
        existing_item = result.scalar_one_or_none()
        
        if existing_item:
            new_quantity = existing_item.quantity + item_data.quantity
            if product.stock < new_quantity:
                raise ValueError(f"Insufficient stock. Available: {product.stock}")
            
            existing_item.quantity = new_quantity
            await session.commit()
            return f"Updated quantity to {new_quantity}"
        else:
            new_item = CartItem(
                user_id=user_id,
                product_id=item_data.product_id,
                quantity=item_data.quantity
            )
            session.add(new_item)
            await session.commit()
            return f"Added '{product.name}' to cart"

    @staticmethod
    async def remove_from_cart(
        session: AsyncSession,
        product_id: int,
        user_id: int
    ) -> bool:
        """Remove a product from cart."""
        query = select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id
        )
        result = await session.execute(query)
        cart_item = result.scalar_one_or_none()
        
        if not cart_item:
            return False
        
        await session.delete(cart_item)
        await session.commit()
        return True

    @staticmethod
    async def clear_cart(
        session: AsyncSession,
        user_id: int
    ) -> None:
        """Clear all items from a user's cart."""
        query = select(CartItem).where(CartItem.user_id == user_id)
        result = await session.execute(query)
        for item in result.scalars().all():
            await session.delete(item)
        await session.commit()