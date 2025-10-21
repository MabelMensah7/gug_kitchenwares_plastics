from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from utils import decode_jwt
from database import db

security = HTTPBearer()
users = db.users

def get_current_user(token: str = Depends(security)):
    try:
        payload = decode_jwt(token.credentials)
        user = users.find_one({"email": payload["email"]})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

def admin_required(user: dict = Depends(get_current_user)):
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
