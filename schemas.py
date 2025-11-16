"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (extend for shop app):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    image: Optional[str] = Field(None, description="Product image URL")
    in_stock: bool = Field(True, description="Whether product is in stock")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    title: str = Field(..., description="Product title at time of purchase")
    price: float = Field(..., ge=0, description="Unit price at time of purchase")
    quantity: int = Field(..., ge=1, description="Quantity of this item")
    image: Optional[str] = Field(None, description="Image URL snapshot")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    customer_name: str = Field(..., description="Customer full name")
    customer_email: EmailStr = Field(..., description="Customer email")
    shipping_address: str = Field(..., description="Shipping address")
    items: List[OrderItem] = Field(..., description="List of items in the order")
    subtotal: float = Field(..., ge=0, description="Subtotal before tax/shipping")
    tax: float = Field(0, ge=0, description="Tax amount")
    total: float = Field(..., ge=0, description="Grand total")
    status: str = Field("pending", description="Order status")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
