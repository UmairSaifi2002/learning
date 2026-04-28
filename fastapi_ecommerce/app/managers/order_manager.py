# """
# Order Manager

# Contains ALL business logic for order operations.

# An order is created from the current cart items.
# This is the most complex manager because it:
# 1. Interacts with CartManager to get/clear the cart
# 2. Interacts with products_db to validate and deduct stock
# 3. Creates order records with their own auto-incrementing IDs

# The order flow:
#     Cart items → Validate → Deduct stock → Create order → Clear cart
# """

# from typing import List
# from datetime import datetime

# from app.data.store import (
#     orders_db,
#     products_db,
#     DEFAULT_USER_ID,
#     next_order_id,
# )

# from app.models.schemas import Order, OrderItem
# from app.managers.cart_manager import CartManager
# from app.utils.loggers import logger


# class OrderManager:
#     """
#     Manager for order-related operations.
    
#     Orders are FINALIZED records of purchases.
#     Once created, they cannot be modified (no update endpoint).
#     You can only view orders (GET) and create them (POST).
    
#     orders_db structure:
#     {
#         1: [                            # user_id = 1
#             Order(
#                 id=1,
#                 items=[OrderItem(...), OrderItem(...)],
#                 total_amount=2105.94,
#                 created_at="2024-01-15T14:30:22"
#             )
#         ]
#     }
#     """
    
#     # Internal order ID counter
#     _order_id_counter: int = next_order_id

#     @classmethod
#     def get_all_orders(
#         cls,
#         user_id: int = DEFAULT_USER_ID
#     ) -> List[Order]:
#         """
#         Get all orders for a user.
        
#         Args:
#             user_id: The user whose orders to retrieve
        
#         Returns:
#             List[Order]: List of orders (newest first)
#         """
#         logger.info(f"Fetching orders for user: {user_id}")
        
#         # Get the user's orders, or empty list if they have none
#         if user_id not in orders_db:
#             orders_db[user_id] = []
        
#         logger.debug(
#             f"User {user_id} has {len(orders_db[user_id])} orders"
#         )
        
#         return orders_db[user_id]
    
#     @classmethod
#     def create_order(
#         cls,
#         user_id: int = DEFAULT_USER_ID
#     ) -> Order:
#         """
#         Create an order from the current cart items.
        
#         This is a TRANSACTION - all steps must succeed.
#         If validation fails, NO changes are made to stock or orders.
        
#         Process:
#         1. Get the user's cart from CartManager
#         2. Check cart is not empty
#         3. Validate every item (existence + stock)
#         4. Deduct stock from inventory
#         5. Create order record
#         6. Clear the cart
#         7. Return the completed order
        
#         Args:
#             user_id: The user placing the order
        
#         Returns:
#             Order: The completed order with ID and timestamp
        
#         Raises:
#             ValueError: If cart is empty, product missing, or insufficient stock
#         """
#         logger.info(f"Creating order for user: {user_id}")

#         # STEP 1: Get the current cart
#         # We call CartManager instead of reading cart_db directly
#         # This keeps the separation of concerns clean
#         cart = CartManager.get_cart(user_id)

#         # STEP 2: Check cart is not empty
#         # You can't place an order with nothing in your cart!
#         if not cart.items:
#             logger.warning("Cannot create order: Cart is empty")
#             raise ValueError("Cannot create order with empty cart")
        
#         # STEP 3: Validate ALL items exist and have sufficient stock
#         # This validates everything BEFORE making any changes
#         # If one item fails, we haven't changed anything yet
#         for cart_item in cart.items:
#             product = products_db.get(cart_item.product_id)
            
#             # Check if product still exists
#             # Product might have been deleted while in user's cart
#             if not product:
#                 logger.error(
#                     f"Product {cart_item.product_id} "
#                     f"('{cart_item.product_name}') no longer exists"
#                 )
#                 raise ValueError(
#                     f"Product '{cart_item.product_name}' "
#                     f"(ID: {cart_item.product_id}) no longer exists. "
#                     f"Please remove it from your cart."
#                 )
            
#             # Check if enough stock is available
#             # Stock might have changed since item was added to cart
#             if product.stock < cart_item.quantity:
#                 logger.error(
#                     f"Insufficient stock for '{product.name}': "
#                     f"available={product.stock}, "
#                     f"requested={cart_item.quantity}"
#                 )
#                 raise ValueError(
#                     f"Insufficient stock for '{product.name}'. "
#                     f"Available: {product.stock}, "
#                     f"Requested: {cart_item.quantity}"
#                 )
            
#         # STEP 4: Deduct stock from inventory
#         # Only reaches here if ALL items passed validation
#         for cart_item in cart.items:
#             product = products_db[cart_item.product_id]
#             product.stock -= cart_item.quantity
#             logger.debug(
#                 f"Deducted {cart_item.quantity} from "
#                 f"'{product.name}'. Remaining stock: {product.stock}"
#             )
        
#         # STEP 5: Create order item records from cart items
#         # Order items are LIKE cart items but for a finalized order
#         # They capture the price AT THE TIME OF ORDER (important!)
#         order_items = []
#         for item in cart.items:
#             order_item = OrderItem(product_id=item.product_id, product_name=item.product_name, quantity=item.quantity, unit_price=item.unit_price, total_price=item.total_price)
#             order_items.append(order_item)
        
#         # STEP 6: Create the order with all items
#         order_id = cls._order_id_counter
#         cls._order_id_counter += 1
        
#         order = Order(id=order_id, items=order_items, total_amount=cart.total_amount, created_at=datetime.now().isoformat() )

#         # STEP 7: Save order to database
#         if user_id not in orders_db:
#             orders_db[user_id] = []
#         orders_db[user_id].append(order)
        
#         logger.info(
#             f"Order created: ID {order_id}, "
#             f"{len(order_items)} items, "
#             f"total ${order.total_amount:.2f}"
#         )

"""
Order Manager

Contains ALL business logic for order operations.

An order is created from the current cart items.
This is the most complex manager because it:
1. Interacts with CartManager to get/clear the cart
2. Interacts with products_db to validate and deduct stock
3. Creates order records with their own auto-incrementing IDs

The order flow:
    Cart items → Validate → Deduct stock → Create order → Clear cart
"""

from typing import List
from datetime import datetime

from app.data.store import (
    orders_db,
    products_db,
    DEFAULT_USER_ID,
    next_order_id,
)

from app.models.schemas import Order, OrderItem
from app.managers.cart_manager import CartManager
from app.utils.loggers import logger  # ← FIXED: "logger" not "loggers"


class OrderManager:
    """
    Manager for order-related operations.
    
    Orders are FINALIZED records of purchases.
    Once created, they cannot be modified (no update endpoint).
    You can only view orders (GET) and create them (POST).
    
    orders_db structure:
    {
        1: [                            # user_id = 1
            Order(
                id=1,
                items=[OrderItem(...), OrderItem(...)],
                total_amount=2105.94,
                created_at="2024-01-15T14:30:22"
            )
        ]
    }
    """
    
    # Internal order ID counter
    _order_id_counter: int = next_order_id

    @classmethod
    def get_all_orders(
        cls,
        user_id: int = DEFAULT_USER_ID
    ) -> List[Order]:
        """
        Get all orders for a user.
        
        Args:
            user_id: The user whose orders to retrieve
        
        Returns:
            List[Order]: List of orders
        """
        logger.info(f"Fetching orders for user: {user_id}")
        
        # Get the user's orders, or empty list if they have none
        if user_id not in orders_db:
            orders_db[user_id] = []
        
        logger.debug(
            f"User {user_id} has {len(orders_db[user_id])} orders"
        )
        
        return orders_db[user_id]
    
    @classmethod
    def create_order(
        cls,
        user_id: int = DEFAULT_USER_ID
    ) -> Order:
        """
        Create an order from the current cart items.
        
        This is a TRANSACTION - all steps must succeed.
        If validation fails, NO changes are made to stock or orders.
        
        Process:
        1. Get the user's cart from CartManager
        2. Check cart is not empty
        3. Validate every item (existence + stock)
        4. Deduct stock from inventory
        5. Create order record
        6. Clear the cart
        7. Return the completed order
        
        Args:
            user_id: The user placing the order
        
        Returns:
            Order: The completed order with ID and timestamp
        
        Raises:
            ValueError: If cart is empty, product missing, or insufficient stock
        """
        logger.info(f"Creating order for user: {user_id}")

        # STEP 1: Get the current cart
        # CartManager.get_cart() returns a Cart OBJECT
        # cart.items contains CartItem OBJECTS (not dicts)
        # So we can use .product_id, .quantity, etc.
        cart = CartManager.get_cart(user_id)

        # STEP 2: Check cart is not empty
        if not cart.items:
            logger.warning("Cannot create order: Cart is empty")
            raise ValueError("Cannot create order with empty cart")
        
        # STEP 3: Validate ALL items exist and have sufficient stock
        # cart_item is a CartItem OBJECT → dot notation WORKS
        # product is a DICT from products_db → use BRACKET notation
        for cart_item in cart.items:
            product = products_db.get(cart_item.product_id)
            
            # Check if product still exists
            if not product:
                logger.error(
                    f"Product {cart_item.product_id} "
                    f"('{cart_item.product_name}') no longer exists"
                )
                raise ValueError(
                    f"Product '{cart_item.product_name}' "
                    f"(ID: {cart_item.product_id}) no longer exists. "
                    f"Please remove it from your cart."
                )
            
            # Check if enough stock is available
            # product is a DICT → use BRACKET notation
            # cart_item is a CartItem OBJECT → use DOT notation
            if product["stock"] < cart_item.quantity:                          # ← FIXED
                logger.error(
                    f"Insufficient stock for '{product['name']}': "            # ← FIXED
                    f"available={product['stock']}, "                          # ← FIXED
                    f"requested={cart_item.quantity}"
                )
                raise ValueError(
                    f"Insufficient stock for '{product['name']}'. "           # ← FIXED
                    f"Available: {product['stock']}, "                         # ← FIXED
                    f"Requested: {cart_item.quantity}"
                )
            
        # STEP 4: Deduct stock from inventory
        # Only reaches here if ALL items passed validation
        for cart_item in cart.items:
            product = products_db[cart_item.product_id]
            product["stock"] -= cart_item.quantity                              # ← FIXED
            logger.debug(
                f"Deducted {cart_item.quantity} from "
                f"'{product['name']}'. Remaining stock: {product['stock']}"    # ← FIXED
            )
        
        # STEP 5: Create order item records from cart items
        # cart_item is a CartItem OBJECT → dot notation works
        order_items = []
        for item in cart.items:
            order_item = OrderItem(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
            )
            order_items.append(order_item)
        
        # STEP 6: Create the order with all items
        order_id = cls._order_id_counter
        cls._order_id_counter += 1
        
        order = Order(
            id=order_id,
            items=order_items,
            total_amount=cart.total_amount,
            created_at=datetime.now().isoformat()
        )

        # STEP 7: Save order to database
        if user_id not in orders_db:
            orders_db[user_id] = []
        orders_db[user_id].append(order)
        
        # STEP 8: Clear the cart (This was MISSING!)
        CartManager.clear_cart(user_id)
        
        logger.info(
            f"Order created: ID {order_id}, "
            f"{len(order_items)} items, "
            f"total ${order.total_amount:.2f}"
        )
        
        # STEP 9: RETURN THE ORDER (This was MISSING!)
        return order

    










