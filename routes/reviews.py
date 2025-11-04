from fastapi import APIRouter, Depends, HTTPException
from bson.objectid import ObjectId
from models import ProductReview, RestockSubscription
from database import db
from dependencies import get_current_user, admin_required
from utils import send_notification, points_for_review

router = APIRouter()
reviews = db.reviews
subscriptions = db.subscriptions
products = db.products
users = db.users

# Submit a review (user)
@router.post("/reviews/")
def submit_review(review: ProductReview, user: dict = Depends(get_current_user)):
    if not products.find_one({"_id": ObjectId(review.product_id)}):
        raise HTTPException(status_code=404, detail="Product not found")

    reviews.insert_one({
        "product_id": review.product_id,
        "user_email": user["email"],
        "rating": review.rating,
        "comment": review.comment,
        "detailed": review.detailed,
        "voted_helpful": review.voted_helpful,
        "approved": False
    })
    return {"message": "Review submitted for admin approval"}

# Approve review (admin)
@router.put("/reviews/{review_id}/approve", dependencies=[Depends(admin_required)])
def approve_review(review_id: str):
    review = reviews.find_one({"_id": ObjectId(review_id)})
    if not review or review.get("approved"):
        raise HTTPException(status_code=404, detail="Review not found or already approved")

    reviews.update_one({"_id": ObjectId(review_id)}, {"$set": {"approved": True}})

    # Award points
    user_email = review["user_email"]
    points = points_for_review(review.get("rating", 1), review.get("detailed", False), review.get("voted_helpful", False))
    users.update_one({"email": user_email}, {"$inc": {"points": points}})

    return {"message": "Review approved", "points_awarded": points}

# Subscribe for restock notifications
@router.post("/subscribe-restock/")
def subscribe_restock(subscription: RestockSubscription):
    if subscriptions.find_one({"product_id": subscription.product_id, "email": subscription.email}):
        return {"message": "Already subscribed"}
    
    subscriptions.insert_one(subscription.dict())
    return {"message": "Subscribed for restock notifications"}
