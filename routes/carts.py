from fastapi import APIRouter, Depends
from models import CartItem
from database import db
from dependencies import get_current_user

router = APIRouter()
carts = db.carts

@router.post("/")
def add_to_cart(item: CartItem, user: dict = Depends(get_current_user)):
    cart = carts.find_one({"email": user["email"]})
    if cart:
        cart["items"].append(item.dict())
        carts.update_one({"email": user["email"]}, {"$set": {"items": cart["items"]}})
    else:
        carts.insert_one({"email": user["email"], "items": [item.dict()]})
    return {"message": "Item added to cart"}

@router.get("/")
def get_cart(user: dict = Depends(get_current_user)):
    cart = carts.find_one({"email": user["email"]})
    return cart if cart else {"items": []}
