from fastapi import APIRouter, Depends, HTTPException
from bson.objectid import ObjectId
from dependencies import get_current_user
from database import db
from utils import points_for_purchase, send_notification

router = APIRouter()
users = db.users
carts = db.carts
products = db.products
orders = db.orders

@router.post("/checkout")
def complete_purchase(user: dict = Depends(get_current_user)):
    cart = carts.find_one({"email": user["email"]})
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0
    updated_products = []

    for item in cart["items"]:
        product = products.find_one({"_id": ObjectId(item["product_id"])})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item['product_id']} not found")
        if item["quantity"] > product.get("stock", 0):
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product['name']}")
        total_amount += product["price"] * item["quantity"]
        updated_products.append({"_id": product["_id"], "new_stock": product["stock"] - item["quantity"]})

    for p in updated_products:
        products.update_one({"_id": p["_id"]}, {"$set": {"stock": p["new_stock"]}})

    order_data = {
        "email": user["email"],
        "items": cart["items"],
        "total_amount": total_amount,
        "status": "completed"
    }
    orders.insert_one(order_data)

    points = points_for_purchase(total_amount)
    users.update_one({"email": user["email"]}, {"$inc": {"points": points}})

    carts.update_one({"email": user["email"]}, {"$set": {"items": []}})

    send_notification(user["email"], f"Purchase completed! You earned {points} points.")

    return {"message": "Purchase completed successfully", "total_amount": total_amount, "points_awarded": points}
