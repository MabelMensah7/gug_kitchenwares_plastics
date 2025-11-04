from fastapi import APIRouter, Depends, HTTPException
from models import CartItem
from database import db
from dependencies import get_current_user
from bson.objectid import ObjectId

router = APIRouter()
carts = db.carts
products = db.products

# Add or update item in cart
@router.post("/")
def add_to_cart(item: CartItem, user: dict = Depends(get_current_user)):
    product = products.find_one({"_id": ObjectId(item.product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be > 0")
    if item.quantity > product.get("stock", 0):
        raise HTTPException(status_code=400, detail="Not enough stock")

    cart = carts.find_one({"email": user["email"]})
    if cart:
        updated = False
        for i in cart["items"]:
            if i["product_id"] == item.product_id:
                i["quantity"] += item.quantity
                updated = True
                break
        if not updated:
            cart["items"].append(item.dict())
        carts.update_one({"email": user["email"]}, {"$set": {"items": cart["items"]}})
    else:
        carts.insert_one({"email": user["email"], "items": [item.dict()]})

    return {"message": "Item added/updated in cart"}

# Get cart
@router.get("/")
def get_cart(user: dict = Depends(get_current_user)):
    cart = carts.find_one({"email": user["email"]})
    if not cart:
        return {"items": []}

    enriched_items = []
    for i in cart["items"]:
        product = products.find_one({"_id": ObjectId(i["product_id"])})
        if product:
            enriched_items.append({
                "product_id": i["product_id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": i["quantity"],
                "stock": product.get("stock", 0)
            })
    return {"items": enriched_items}

# Update quantity
@router.put("/{product_id}")
def update_cart_item(product_id: str, quantity: int, user: dict = Depends(get_current_user)):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be > 0")
    product = products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if quantity > product.get("stock", 0):
        raise HTTPException(status_code=400, detail="Not enough stock")

    cart = carts.find_one({"email": user["email"]})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart is empty")

    found = False
    for i in cart["items"]:
        if i["product_id"] == product_id:
            i["quantity"] = quantity
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Product not in cart")

    carts.update_one({"email": user["email"]}, {"$set": {"items": cart["items"]}})
    return {"message": "Cart updated successfully"}

# Remove item
@router.delete("/{product_id}")
def remove_cart_item(product_id: str, user: dict = Depends(get_current_user)):
    cart = carts.find_one({"email": user["email"]})
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=404, detail="Cart is empty")

    new_items = [i for i in cart["items"] if i["product_id"] != product_id]
    carts.update_one({"email": user["email"]}, {"$set": {"items": new_items}})
    return {"message": "Item removed from cart"}
