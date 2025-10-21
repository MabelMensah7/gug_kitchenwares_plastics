from pydantic import BaseModel, EmailStr
from typing import Optional

# User
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_admin: Optional[bool] = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Product
class Product(BaseModel):
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str] = None
    image_url: Optional[str] = None

# Cart
class CartItem(BaseModel):
    product_id: str
    quantity: int
