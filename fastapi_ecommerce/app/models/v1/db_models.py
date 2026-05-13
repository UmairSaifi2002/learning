"""
Database Models - SQLAlchemy 2.0 ORM

This file defines ALL database tables using SQLAlchemy ORM.
Each class represents a MySQL table.
Relationships (Foreign Keys) connect the tables together.

Architecture:
- Base: Parent class from app.db.database
- Each model inherits from Base
- Each model has __tablename__ (MySQL table name)
- Relationships use ForeignKey and relationship()
"""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from fastapi_ecommerce.app.db.v1.base import Base


# ============================================
# ENUMS
# ============================================

class OrderStatus(str, enum.Enum):
    """Possible states for an order."""
    PENDING = "pending"         # Order created, not yet processed
    CONFIRMED = "confirmed"     # Order confirmed
    PROCESSING = "processing"   # Order being prepared
    SHIPPED = "shipped"        # Order shipped to customer
    DELIVERED = "delivered"    # Order delivered
    CANCELLED = "cancelled"    # Order cancelled


# ============================================
# USER TABLE
# ============================================

class User(Base):
    """
    User table - stores registered users.
    
    MySQL Columns:
    ┌───────────────┬──────────────┬─────────────────────────────┐
    │ Column        │ Type         │ Description                 │
    ├───────────────┼──────────────┼─────────────────────────────┤
    │ id            │ INT (PK)     │ Auto-incrementing ID        │
    │ name          │ VARCHAR(100) │ User's full name            │
    │ email         │ VARCHAR(255) │ Unique email (login)        │
    │ password_hash │ VARCHAR(255) │ Hashed password (never plain)│
    │ is_active     │ BOOLEAN      │ Whether account is active   │
    │ created_at    │ DATETIME     │ Account creation timestamp  │
    │ updated_at    │ DATETIME     │ Last update timestamp       │
    └───────────────┴──────────────┴─────────────────────────────┘
    
    Relationships:
    - cart_items: Items in this user's shopping cart
    - orders: Orders placed by this user
    """
    __tablename__ = "users"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # User Information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Account Status
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem", back_populates="user", cascade="all, delete-orphan"
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="user", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


# ============================================
# PRODUCT TABLE
# ============================================

class Product(Base):
    """
    Product table - stores the product catalog.
    
    MySQL Columns:
    ┌─────────────┬──────────────┬─────────────────────────────┐
    │ Column      │ Type         │ Description                 │
    ├─────────────┼──────────────┼─────────────────────────────┤
    │ id          │ INT (PK)     │ Auto-incrementing ID        │
    │ name        │ VARCHAR(200) │ Product name (indexed)      │
    │ description │ TEXT         │ Product description         │
    │ price       │ DECIMAL      │ Product price (precise)     │
    │ category    │ VARCHAR(100) │ Product category (indexed)  │
    │ stock       │ INT          │ Available quantity          │
    │ image_url   │ VARCHAR(500) │ Product image URL           │
    │ is_active   │ BOOLEAN      │ Whether product is visible  │
    │ created_at  │ DATETIME     │ Creation timestamp          │
    │ updated_at  │ DATETIME     │ Last update timestamp       │
    └─────────────┴──────────────┴─────────────────────────────┘
    """
    __tablename__ = "products"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Product Information
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem", back_populates="product"
    )
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="product"
    )
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"


# ============================================
# CART ITEM TABLE
# ============================================

class CartItem(Base):
    """
    Cart Item table - stores items in users' shopping carts.
    
    Each row represents ONE product in ONE user's cart.
    A user can have multiple cart items (one per product).
    
    Foreign Keys:
    - user_id → users.id (which user owns this cart item)
    - product_id → products.id (which product is in the cart)
    
    MySQL Columns:
    ┌────────────┬──────────┬─────────────────────────────────┐
    │ Column     │ Type     │ Description                     │
    ├────────────┼──────────┼─────────────────────────────────┤
    │ id         │ INT (PK) │ Auto-incrementing ID            │
    │ user_id    │ INT (FK) │ References users.id             │
    │ product_id │ INT (FK) │ References products.id          │
    │ quantity   │ INT      │ Quantity in cart                │
    │ added_at   │ DATETIME │ When item was added to cart     │
    └────────────┴──────────┴─────────────────────────────────┘
    """
    __tablename__ = "cart_items"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    
    # Cart Information
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    added_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    
    # Relationships (back references)
    user: Mapped["User"] = relationship("User", back_populates="cart_items")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")
    
    def __repr__(self) -> str:
        return f"<CartItem(user={self.user_id}, product={self.product_id}, qty={self.quantity})>"


# ============================================
# ORDER TABLE
# ============================================

class Order(Base):
    """
    Order table - stores completed/pending orders.
    
    Each row represents ONE order placed by ONE user.
    
    Foreign Keys:
    - user_id → users.id (which user placed the order)
    
    MySQL Columns:
    ┌──────────────┬──────────────┬─────────────────────────────┐
    │ Column       │ Type         │ Description                 │
    ├──────────────┼──────────────┼─────────────────────────────┤
    │ id           │ INT (PK)     │ Auto-incrementing ID        │
    │ user_id      │ INT (FK)     │ References users.id         │
    │ status       │ ENUM         │ Order status                │
    │ total_amount │ DECIMAL      │ Total order amount          │
    │ created_at   │ DATETIME     │ Order creation timestamp    │
    │ updated_at   │ DATETIME     │ Last status update          │
    └──────────────┴──────────────┴─────────────────────────────┘
    """
    __tablename__ = "orders"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    
    # Order Information
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False
    )
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Order(id={self.id}, user={self.user_id}, status='{self.status}')>"


# ============================================
# ORDER ITEM TABLE
# ============================================

class OrderItem(Base):
    """
    Order Item table - stores individual items within an order.
    
    Each row represents ONE product in ONE order.
    We SNAPSHOT the product name and price at time of order,
    so historical orders show the correct price even if
    the product price changes later.
    
    Foreign Keys:
    - order_id → orders.id (which order this item belongs to)
    - product_id → products.id (which product was ordered)
    
    MySQL Columns:
    ┌──────────────┬──────────────┬─────────────────────────────┐
    │ Column       │ Type         │ Description                 │
    ├──────────────┼──────────────┼─────────────────────────────┤
    │ id           │ INT (PK)     │ Auto-incrementing ID        │
    │ order_id     │ INT (FK)     │ References orders.id        │
    │ product_id   │ INT (FK)     │ References products.id      │
    │ product_name │ VARCHAR(200) │ Product name at order time  │
    │ quantity     │ INT          │ Quantity ordered            │
    │ unit_price   │ DECIMAL      │ Price per unit at order time│
    │ total_price  │ DECIMAL      │ quantity × unit_price       │
    └──────────────┴──────────────┴─────────────────────────────┘
    """
    __tablename__ = "order_items"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    
    # Order Item Information (SNAPSHOT values)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    
    def __repr__(self) -> str:
        return f"<OrderItem(order={self.order_id}, product='{self.product_name}', qty={self.quantity})>"



