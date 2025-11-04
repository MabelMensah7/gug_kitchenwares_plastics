from fastapi import APIRouter, Depends
from database import db
from dependencies import get_current_user
from utils import profile_completion_progress, is_profile_complete

router = APIRouter(prefix="/profile")
users = db.users

@router.get("/progress")
def get_profile_progress(user: dict = Depends(get_current_user)):
    progress = profile_completion_progress(user)
    return {"progress_percent": progress, "message": f"You are {progress}% complete"}

@router.put("/update")
def update_profile(details: dict, user: dict = Depends(get_current_user)):
    users.update_one({"email": user["email"]}, {"$set": details})
    updated_user = users.find_one({"email": user["email"]})

    points_awarded = 0
    if is_profile_complete(updated_user) and user.get("points_complete_profile") is None:
        points_awarded = 10
        users.update_one({"email": user["email"]}, {"$inc": {"points": points_awarded}, "$set": {"points_complete_profile": True}})

    return {"message": "Profile updated", "points_awarded": points_awarded}
