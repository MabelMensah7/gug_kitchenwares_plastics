from pydantic import BaseModel, EmailStr
from typing import Optional, List

# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "customer"  # roles: admin, staff, customer

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# New schema for updating profile
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[str] = None  # format YYYY-MM-DD
    gender: Optional[str] = None
    alt_address: Optional[str] = None
    phone: Optional[str] = None

# Product schemas
class Product(BaseModel):
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str] = None
    image_url: Optional[str] = None

# Cart schemas
class CartItem(BaseModel):
    product_id: str
    quantity: int

# Review Model
class ProductReview(BaseModel):
    product_id: str
    rating: int  # 1–5
    comment: Optional[str] = None
    detailed: Optional[bool] = False
    voted_helpful: Optional[bool] = False

# Restock Subscription
class RestockSubscription(BaseModel):
    product_id: str
    email: EmailStr
