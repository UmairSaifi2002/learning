"""
Product Manager

This file contains ALL business logic related to products.
The router calls these methods - it never touches the data directly.

Think of the manager as the "brain" and the router as the "door".
The door lets people in; the brain decides what to do with them.
"""

# 1. We import type hints for cleaner code documentation
from typing import List, Optional

# 2. We import our shared data store
#    This is the SAME dictionary that all managers use
#    When we modify it here, the changes are visible everywhere
from app.data.store import products_db, next_product_id as global_next_id

# 3. We import our Pydantic models for validation
from app.models.schemas import ProductCreate, ProductUpdate, Product

# 4. We import our logger to track what's happening
from app.utils.loggers import logger

class ProductManager:
    """
    ProductManager contains all business logic related to products.
    The router calls these methods - it never touches the data directly.
    """

    # Internal ID counter for generating new product IDs
    # Starts from the value in store.py, then auto-increments
    _next_id: int = global_next_id

    @classmethod
    def get_all_products(cls, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Get all products with optional pagination.

        Args:
            skip: Number of products to skip (for pagination)
            limit: Maximum number of products to return

        Returns:
            List[Product]: List of products matching the criteria
        """
        logger.info("Fetching all Products")

        # Convert dictionary values to a list
        # products_db = {1: Product(...), 2: Product(...)}
        # .values() gives us: [Product(...), Product(...)]
        # list() converts the view to an actual list
        products = list(products_db.values())

        # Apply pagination using list slicing
        # [skip:skip+limit] means "start at skip, go up to skip+limit"
        result = products[skip:skip + limit]

        logger.debug(f"Returning {len(result)} products")
        return result
    
    @classmethod
    def get_product(cls, product_id: int) -> Optional[Product]:
        """
        Get a single product by its ID.

        Args:
            product_id: The unique identifier of the product

        Returns:
            Product if found, None if product doesn't exist
        """
        logger.info(f"Looking up product ID: {product_id}")

        # .get() is a dictionary method
        # If key exists → returns the value
        # If key doesn't exist → returns None (instead of crashing)
        product = products_db.get(product_id)

        if product:
            logger.debug(f"Product Found: {product['name']}")
        else:
            logger.warning(f"Product ID {product_id} not Found")
        
        return product
    
    @classmethod
    def create_product(cls, product_data: ProductCreate) -> Product:
        """
        Create a new product in the database.

        Args:
            product_data: Validated product creation data (from request body)

        Returns:
            Product: The newly created product with assigned ID

        Raises:
            Exception: If product creation fails unexpectedly
        """
        logger.info(f"Creating a new product: {product_data.name}")

        try:
            # Generate a new unique ID for the product
            new_id = cls._next_id
            cls._next_id += 1 # Increment the ID for the next product

            new_product = Product(
                id = new_id,
                **product_data.model_dump() # Convert Pydantic model to dict for unpacking
            )

            # Store in the database dictionary
            products_db[new_id] = new_product

            logger.info(f"Product Created Successfully with ID: {new_id}")
            return new_product
        except Exception as e:
            logger.error(f"Error Creating a Product: {str(e)}")
            raise Exception(f"Product creation failed: {str(e)}")
        
    @classmethod
    def update_product(cls, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """
        Update an existing product's details.

        Args:
            product_id: The unique identifier of the product to update
            product_data: Validated product update data (from request body)

        Returns:
            Product if update is successful, None if product doesn't exist

        Raises:
            Exception: If product update fails unexpectedly
        """
        logger.info(f"Updating product ID: {product_id}")

        existing_product = products_db.get(product_id)

        if not existing_product:
            logger.warning(f"Product ID {product_id} not Found for Update")
            return None
        
        try:
            # Get ONLY the fields the client sent (not all fields)
            # exclude_unset=True means: skip fields the client didn't include
            updated_fields = product_data.model_dump(exclude_unset=True)

            # Create updated product
            # For each field: use new value if provided, otherwise keep old value
            updated_product = Product(
                id=product_id,
                name = updated_fields.get("name", existing_product.name),
                price = updated_fields.get("price", existing_product.price),
                category = updated_fields.get("category", existing_product.category),
                stock = updated_fields.get("stock", existing_product.stock)
            )

            # Save to Database
            products_db[product_id] = updated_product

            logger.info(f"Product Updated Successfully: {updated_product.name}")
            return updated_product
        
        except Exception as e:
            logger.error(f"Error Updating Product ID {product_id}: {str(e)}")
            raise Exception(f"Product update failed: {str(e)}")
        
    @classmethod
    def delete_product(cls, product_id: int) -> bool:
        """
        Delete a product from the database.

        Args:
            product_id: The unique identifier of the product to delete
        Returns:
            bool: True if deletion was successful, False if product doesn't exist
        Raises:
            Exception: If product deletion fails unexpectedly
        """
        logger.info(f"Deleting Product ID: {product_id}")
        if product_id not in products_db:
            logger.warning(f"Product Id {product_id} not Found for Deletion")
            return False
        
        product_name = products_db[product_id].name
        del products_db[product_id]
        logger.info(f"Product Deleted Successfully: {product_name}")
        return True
    
    @classmethod
    def product_exists(cls, product_id: int) -> bool:
        """
        Check if a product exists in the database.

        Args:
            product_id: The unique identifier of the product to check
        Returns:
            bool: True if product exists, False otherwise
        """
        return product_id in products_db

















