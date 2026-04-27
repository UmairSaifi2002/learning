"""
Pydantic Models (Schemas) for the E-Commerce API

This file defines ALL data shapes used in our application.
FastAPI uses these models to:
1. Validate incoming requests (is the data correct?)
2. Serialize outgoing responses (convert Python → JSON)
3. Generate OpenAPI documentation automatically

Every class inherits from BaseModel.
Every field has a type hint and optional validation constraints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


# ============================================
# USER SCHEMAS
# ============================================

class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    
    All fields are REQUIRED.
    This is what the client sends in a POST /users request.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's full name",
        examples=["Ahmed Khan"]
    )
    email: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="User's email address",
        examples=["ahmed@example.com"]
    )

class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.
    
    ALL fields are OPTIONAL.
    The client only sends the fields they want to change.
    Fields not sent remain unchanged.
    """
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated name"
    )
    email: Optional[str] = Field(
        None,
        min_length=5,
        max_length=100,
        description="Updated email"
    )

class User(BaseModel):
    """
    Schema for user response.
    
    This is what the API RETURNS to the client.
    Includes the auto-generated 'id' field.
    """
    id: int = Field(..., description="Unique user ID")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email")


# ============================================
# PRODUCT SCHEMAS
# ============================================

class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Product name",
        examples=["Wireless Mouse"]
    )
    price: float = Field(
        ...,
        gt=0,
        description="Product price (must be positive)",
        examples=[29.99]
    )
    category: str = Field(
        ...,
        min_length=1,
        description="Product category",
        examples=["Electronics"]
    )
    stock: int = Field(
        default=0,
        ge=0,
        description="Available stock (cannot be negative)",
        examples=[100]
    )

class ProductUpdate(BaseModel):
    """Schema for updating a product. All fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1)
    stock: Optional[int] = Field(None, ge=0)

class Product(BaseModel):
    """Schema for product response."""
    id: int
    name: str
    price: float
    category: str
    stock: int

# ============================================
# CART ORDER SCHEMAS
# ============================================

class CartItemAdd(BaseModel):
    """
    Schema for adding an item to cart.
    
    The client only sends product_id and quantity.
    We calculate prices on the server (prevents manipulation).
    """
    product_id: int = Field(
        ...,
        gt=0,
        description="ID of the product to add to cart",
        examples=[1]
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity to add (must be at least 1)",
        examples=[2]
    )

class CartItem(BaseModel):
    """
    Schema for cart item response.
    
    Includes calculated fields that the server generates.
    """
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_price: float

class Cart(BaseModel):
    """
    Schema for full cart response.
    
    Shows all items plus summary totals.
    """
    items: List[CartItem] = Field(
        default_factory=list,
        description="List of items in cart"
    )
    total_items: int = Field(
        default=0,
        description="Total number of items"
    )
    total_amount: float = Field(
        default=0.0,
        description="Total price of all items"
    )

# ============================================


class OrderItem(BaseModel):
    """
    Schema for a single item within an order.
    
    Similar to CartItem but for finalized orders.
    """
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_price: float

class Order(BaseModel):
    """Schema for order response."""
    id: int
    items: List[OrderItem]
    total_amount: float
    created_at: str

# ============================================

class MessageResponse(BaseModel):
    """
    Generic success/error message response.
    
    Used for operations that don't return data,
    just a confirmation message (like DELETE).
    """
    message: str = Field(..., description="Response message")
    detail: Optional[str] = Field(
        None,
        description="Additional details (optional)"
    )




