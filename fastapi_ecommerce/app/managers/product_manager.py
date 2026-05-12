"""
Product Manager - MySQL Database Version

All business logic for products, now using SQLAlchemy async sessions
instead of in-memory dictionaries.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Product
from app.models.schemas import ProductCreate, ProductUpdate
from app.utils.loggers import logger


class ProductManager:
    """
    Manager for product-related operations.
    
    ALL methods now require an AsyncSession parameter.
    The session is provided by FastAPI via dependency injection.
    """

    @staticmethod
    async def get_all_products(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Get all products with optional pagination.
        
        Args:
            session: Database session (injected by FastAPI)
            skip: Number of products to skip
            limit: Maximum number of products to return
        
        Returns:
            List[Product]: List of Product ORM objects
        """
        logger.info("Fetching all products from database")
        
        # Build the SELECT query
        # select(Product) generates: SELECT * FROM products
        # .offset(skip) adds: OFFSET skip
        # .limit(limit) adds: LIMIT limit
        query = select(Product).offset(skip).limit(limit)
        
        # Execute the query asynchronously
        # await because this is an I/O operation (talking to MySQL)
        result = await session.execute(query)
        
        # Extract Product objects from the result
        # scalars() gets the first column of each row as Python objects
        # all() converts to a list
        products = result.scalars().all()
        
        logger.info(f"Returning {len(products)} products")
        return products

    @staticmethod
    async def get_product(
        session: AsyncSession,
        product_id: int
    ) -> Optional[Product]:
        """
        Get a single product by ID.
        
        Args:
            session: Database session
            product_id: Product ID
        
        Returns:
            Product if found, None otherwise
        """
        logger.info(f"Looking up product ID: {product_id}")
        
        # session.get() is the fastest way to get by primary key
        # It first checks the session cache, then queries the database
        product = await session.get(Product, product_id)
        
        if product:
            logger.debug(f"Found product: {product.name}")
        else:
            logger.warning(f"Product not found: ID {product_id}")
        
        return product

    @staticmethod
    async def create_product(
        session: AsyncSession,
        product_data: ProductCreate
    ) -> Product:
        """
        Create a new product.
        
        Args:
            session: Database session
            product_data: Validated product data (Pydantic model)
        
        Returns:
            Product: The newly created product with generated ID
        """
        logger.info(f"Creating new product: {product_data.name}")
        
        try:
            # Convert Pydantic model to dictionary
            # Create a new Product ORM instance
            new_product = Product(**product_data.model_dump())
            
            # Add to the session (stages the INSERT)
            session.add(new_product)
            
            # Commit the transaction (executes the INSERT SQL)
            await session.commit()
            
            # Refresh to get the auto-generated ID and timestamps
            await session.refresh(new_product)
            
            logger.info(f"Product created: ID {new_product.id}")
            return new_product
            
        except Exception as e:
            # Rollback on any error
            await session.rollback()
            logger.error(f"Failed to create product: {str(e)}")
            raise Exception(f"Product creation failed: {str(e)}")

    @staticmethod
    async def update_product(
        session: AsyncSession,
        product_id: int,
        product_data: ProductUpdate
    ) -> Optional[Product]:
        """
        Update an existing product.
        
        Only updates fields that were provided.
        Fields not provided remain unchanged.
        
        Args:
            session: Database session
            product_id: ID of the product to update
            product_data: New data (only provided fields)
        
        Returns:
            Updated Product if found, None otherwise
        """
        logger.info(f"Updating product ID: {product_id}")
        
        # Find the existing product
        product = await session.get(Product, product_id)
        if not product:
            logger.warning(f"Product not found: ID {product_id}")
            return None
        
        try:
            # Get only the fields the client sent
            update_dict = product_data.model_dump(exclude_unset=True)
            
            # Update attributes on the ORM object
            # SQLAlchemy tracks these changes automatically
            if "name" in update_dict:
                product.name = update_dict["name"]
            if "price" in update_dict:
                product.price = update_dict["price"]
            if "category" in update_dict:
                product.category = update_dict["category"]
            if "stock" in update_dict:
                product.stock = update_dict["stock"]
            
            # Commit the changes (generates UPDATE SQL)
            await session.commit()
            await session.refresh(product)
            
            logger.info(f"Product updated: ID {product_id}")
            return product
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to update product: {str(e)}")
            raise Exception(f"Product update failed: {str(e)}")

    @staticmethod
    async def delete_product(
        session: AsyncSession,
        product_id: int
    ) -> bool:
        """
        Delete a product.
        
        Args:
            session: Database session
            product_id: ID of the product to delete
        
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting product ID: {product_id}")
        
        product = await session.get(Product, product_id)
        if not product:
            logger.warning(f"Product not found: ID {product_id}")
            return False
        
        try:
            await session.delete(product)
            await session.commit()
            logger.info(f"Product deleted: ID {product_id}")
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to delete product: {str(e)}")
            raise Exception(f"Product deletion failed: {str(e)}")

    @staticmethod
    async def product_exists(
        session: AsyncSession,
        product_id: int
    ) -> bool:
        """Check if a product exists."""
        product = await session.get(Product, product_id)
        return product is not None
    



