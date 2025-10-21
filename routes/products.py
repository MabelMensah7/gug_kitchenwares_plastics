from fastapi import APIRouter
from bson.objectid import ObjectId
from database import db

router = APIRouter()
products = db.products

# Get all products (public)
@router.get("/")
def list_products():
    result = []
    for p in products.find():
        p["_id"] = str(p["_id"]) 
        result.append(p)
    return result


# Get one product by ID (public)
@router.get("/{product_id}")
def get_product(product_id: str):
    p = products.find_one({"_id": ObjectId(product_id)})
    if not p:
        return {"error": "Product not found"}
    p["_id"] = str(p["_id"])  
    return p
