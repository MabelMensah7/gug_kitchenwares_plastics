from fastapi import APIRouter, HTTPException, Depends
from models import UserCreate, UserLogin, UserUpdate
from utils import hash_password, verify_password, create_jwt, profile_completion_progress
from database import db
from dependencies import get_current_user

router = APIRouter()
users = db.users

# -----------------------------
# Signup
# -----------------------------
@router.post("/signup")
def signup(user: UserCreate):
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    hashed = hash_password(user.password)
    users.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed,
        "role": user.role,
        "points": 0
    })
    return {"message": f"{user.role.capitalize()} account created successfully"}

# -----------------------------
# Login
# -----------------------------
@router.post("/login")
def login(user: UserLogin):
    db_user = users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt({"email": user.email})
    return {
        "token": token,
        "username": db_user["username"],
        "role": db_user.get("role", "customer"),
        "points": db_user.get("points", 0)
    }

# -----------------------------
# Update profile
# -----------------------------
@router.put("/update-profile")
def update_profile(data: UserUpdate, user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in data.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    users.update_one({"email": user["email"]}, {"$set": update_data})

    # Return updated profile completion percentage
    updated_user = users.find_one({"email": user["email"]})
    progress = profile_completion_progress(updated_user)

    return {
        "message": "Profile updated successfully",
        "profile_completion": f"{progress}%"
    }
