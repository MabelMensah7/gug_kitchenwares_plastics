from fastapi import APIRouter, Depends, HTTPException
from bson.objectid import ObjectId
from models import Product
from dependencies import get_current_user, admin_required, staff_required
from database import db
from utils import send_notification

router = APIRouter()
products = db.products
subscriptions = db.subscriptions

# Admin: add product
@router.post("/", dependencies=[Depends(admin_required)])
def add_product(product: Product):
    result = products.insert_one(product.dict())
    return {"message": "Product added successfully", "id": str(result.inserted_id)}

# Admin: update product fully
@router.put("/{product_id}", dependencies=[Depends(admin_required)])
def update_product(product_id: str, product: Product):
    result = products.update_one({"_id": ObjectId(product_id)}, {"$set": product.dict()})
    if result.modified_count == 0:
        return {"error": "Product not found or nothing changed"}

    # Notify subscribers if stock > 0
    if product.stock > 0:
        subs = subscriptions.find({"product_id": product_id})
        for sub in subs:
            send_notification(sub["email"], f"The product '{product.name}' is back in stock!")
            subscriptions.delete_one({"_id": sub["_id"]})

    return {"message": "Product updated successfully"}

# Admin: delete product
@router.delete("/{product_id}", dependencies=[Depends(admin_required)])
def delete_product(product_id: str):
    result = products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# Public: list products
@router.get("/")
def list_products():
    result = []
    for p in products.find():
        p["_id"] = str(p["_id"])
        result.append(p)
    return result

# Public: get single product
@router.get("/{product_id}")
def get_product(product_id: str):
    p = products.find_one({"_id": ObjectId(product_id)})
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    p["_id"] = str(p["_id"])
    return p

# Staff: update stock only
@router.patch("/{product_id}/stock")
def update_stock(product_id: str, stock: int, user: dict = Depends(get_current_user)):
    if not (user.get("is_staff", False) or user.get("is_admin", False)):
        raise HTTPException(status_code=403, detail="Staff or Admin access required")
    if stock < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative")
    result = products.update_one({"_id": ObjectId(product_id)}, {"$set": {"stock": stock}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Stock updated successfully"}
