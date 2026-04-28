"""
Cart Manager

Contains ALL business logic for shopping cart operations.

The cart is different from products and users:
- Cart items belong to a USER (not a standalone entity)
- Cart items reference products (we verify product exists and has stock)
- Cart calculates prices server-side (prevents client manipulation)
- Cart items have NO auto-generated ID (identified by product_id)
"""

from typing import Optional
from app.data.store import (
    cart_db,
    products_db,
    DEFAULT_USER_ID,
)
from app.models.schemas import (
    CartItem,
    CartItemAdd,
    Cart,
)
from app.utils.loggers import logger


class CartManager:
    """
    Manager for cart-related operations.
    
    The cart stores a LIST of items per user, not a dictionary by ID.
    This is because cart items don't have their own IDs - they are
    identified by the product_id they contain.
    
    cart_db structure:
    {
        1: [                            # user_id = 1
            CartItem(product_id=1, ...),  # Laptop
            CartItem(product_id=3, ...),  # USB Cable
        ]
    }
    """

    @classmethod
    def _get_user_cart(cls, user_id: int = DEFAULT_USER_ID) -> list:
        """
        Get or create a cart for a specific user.
        
        This is a PRIVATE method (underscore prefix).
        It should NOT be called from routers.
        Other manager methods use this to access the cart.
        
        Args:
            user_id: The user whose cart we want
        
        Returns:
            list: The cart items list (empty list if new user)
        """
        # If this user doesn't have a cart yet, create an empty one
        if user_id not in cart_db:
            cart_db[user_id] = []
        
        # Return the user's cart list
        return cart_db[user_id]
    
    @classmethod
    def get_cart(cls, user_id: int = DEFAULT_USER_ID) -> Cart:
        """
        Get the full cart with calculated totals.
        
        This method:
        1. Retrieves all items in the user's cart
        2. Calculates total_items (sum of quantities)
        3. Calculates total_amount (sum of total_prices)
        4. Returns a Cart object with summary
        
        Args:
            user_id: The user whose cart to retrieve
        
        Returns:
            Cart: Cart object containing items and summary totals
        """
        logger.info(f"Getting cart for user: {user_id}")
        
        # Get the list of cart items
        cart_items = cls._get_user_cart(user_id)
        
        # Calculate summary statistics
        # These are DERIVED values - we don't store them, we calculate them
        total_items = sum(item.quantity for item in cart_items)
        total_amount = sum(item.total_price for item in cart_items)
        
        logger.debug(
            f"Cart has {total_items} items, total: ${total_amount:.2f}"
        )
        
        # Return a Cart object with items and calculated totals
        return Cart(
            items=cart_items,
            total_items=total_items,
            total_amount=round(total_amount, 2)
        )
    
    @classmethod
    def add_to_cart(
        cls,
        item_data: CartItemAdd,
        user_id: int = DEFAULT_USER_ID
    ) -> str:
        """
        Add a product to the cart.
        
        Business rules:
        1. Product must exist in products_db
        2. Product must have sufficient stock
        3. If product already in cart, increase quantity
        4. If product is new to cart, add as new item
        5. Prices are ALWAYS looked up from products_db (not from client)
        
        Args:
            item_data: Contains product_id and quantity
            user_id: The user adding to cart
        
        Returns:
            str: Success message describing what happened
        
        Raises:
            ValueError: If product not found or insufficient stock
        """
        logger.info(
            f"Adding to cart: product_id={item_data.product_id}, "
            f"quantity={item_data.quantity}"
        )
    
        # VALIDATION STEP 1: Does the product exist?
        # product is a DICTIONARY, not a Product object
        product = products_db.get(item_data.product_id)
        if not product:
            logger.error(
                f"Cannot add to cart: Product ID {item_data.product_id} not found"
            )
            raise ValueError(
                f"Product with ID {item_data.product_id} not found"
            )
        
        # VALIDATION STEP 2: Is there enough stock?
        # Use BRACKET notation because product is a dict
        if product["stock"] < item_data.quantity:                          # ← FIXED
            logger.error(
                f"Insufficient stock for '{product['name']}': "            # ← FIXED
                f"requested={item_data.quantity}, available={product['stock']}"  # ← FIXED
            )
            raise ValueError(
                f"Insufficient stock for '{product['name']}'. "           # ← FIXED
                f"Available: {product['stock']}, Requested: {item_data.quantity}"  # ← FIXED
            )
        
        # Get the user's cart (creates empty list if first time)
        cart_items = cls._get_user_cart(user_id)
    
        # Check if this product is already in the cart
        existing_item = next(
            (item for item in cart_items if item.product_id == item_data.product_id), None
        )
    
        if existing_item:
            # Product is ALREADY in cart - increase quantity
            new_quantity = existing_item.quantity + item_data.quantity
            
            # Double-check stock for the new total quantity
            if product["stock"] < new_quantity:                           # ← FIXED
                raise ValueError(
                    f"Insufficient stock for '{product['name']}'. "      # ← FIXED
                    f"Available: {product['stock']}, "                   # ← FIXED
                    f"Requested: {new_quantity} "
                    f"(already had {existing_item.quantity} in cart)"
                )
            
            # Update the existing item
            existing_item.quantity = new_quantity
            existing_item.total_price = round(
                new_quantity * product["price"], 2                        # ← FIXED
            )
            
            logger.info(
                f"Updated '{product['name']}' quantity to {new_quantity}"  # ← FIXED
            )
            return (
                f"Updated '{product['name']}' quantity to {new_quantity}. "  # ← FIXED
                f"Total price: ${existing_item.total_price:.2f}"
            )
    
        else:
            # Product is NOT in cart yet - add as new item
            new_item = CartItem(
                product_id=item_data.product_id,
                product_name=product["name"],                              # ← FIXED
                quantity=item_data.quantity,
                unit_price=product["price"],                               # ← FIXED
                total_price=round(item_data.quantity * product["price"], 2)  # ← FIXED
            )
            
            cart_items.append(new_item)
            
            logger.info(
                f"Added '{product['name']}' to cart (qty: {item_data.quantity})"  # ← FIXED
            )
            return (
                f"Added '{product['name']}' to cart. "                     # ← FIXED
                f"Quantity: {item_data.quantity}, "
                f"Total price: ${new_item.total_price:.2f}"
            )

    @classmethod
    def remove_from_cart(
        cls,
        product_id: int,
        user_id: int = DEFAULT_USER_ID
    ) -> bool:
        """
        Remove a product from the cart.
        
        Args:
            product_id: The product ID to remove
            user_id: The user whose cart to modify
        
        Returns:
            bool: True if item was removed, False if not found in cart
        """
        logger.info(f"Removing product_id={product_id} from cart")
        
        cart_items = cls._get_user_cart(user_id)
        initial_count = len(cart_items)
        
        # Keep all items EXCEPT the one with matching product_id
        cart_db[user_id] = [
            item for item in cart_items
            if item.product_id != product_id
        ]
        
        # Check if anything was actually removed
        removed = len(cart_db[user_id]) < initial_count
        
        if removed:
            logger.info(f"Product {product_id} removed from cart")
        else:
            logger.warning(f"Product {product_id} not found in cart")
        
        return removed
    
    @classmethod
    def clear_cart(cls, user_id: int = DEFAULT_USER_ID) -> None:
        """
        Clear all items from the cart.
        
        Used after an order is placed successfully.
        
        Args:
            user_id: The user whose cart to clear
        """
        logger.info(f"Clearing cart for user: {user_id}")
        cart_db[user_id] = []










