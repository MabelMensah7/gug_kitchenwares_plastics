from fastapi import APIRouter, HTTPException
from models import UserCreate, UserLogin
from utils import hash_password, verify_password, create_jwt
from database import db

router = APIRouter()
users = db.users

@router.post("/signup")
def signup(user: UserCreate):
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed = hash_password(user.password)
    users.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed,
        "is_admin": user.is_admin
    })
    return {"message": "User created successfully"}

@router.post("/login")
def login(user: UserLogin):
    db_user = users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt({"email": user.email})
    return {"token": token, "username": db_user["username"], "is_admin": db_user.get("is_admin", False)}
