import bcrypt
from jose import jwt
from database import JWT_SECRET, JWT_ALGORITHM

# Password hashing
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode())

# JWT functions
def create_jwt(payload: dict) -> str:
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

# -----------------------------
# Gamification / Points
# -----------------------------
def points_for_purchase(amount: float) -> int:
    if amount < 100:
        return 1
    elif amount < 500:
        return 5
    elif amount < 1000:
        return 10
    elif amount < 2000:
        return 20
    else:
        return 40

def points_for_review(rating: int, detailed: bool = False, voted_helpful: bool = False) -> int:
    points = rating
    if detailed or voted_helpful:
        points += 4
    return points

def profile_completion_progress(user: dict) -> int:
    fields = ["username", "email", "location", "dob"]
    completed = sum(1 for f in fields if user.get(f))
    return int((completed / len(fields)) * 100)

def is_profile_complete(user: dict) -> bool:
    return profile_completion_progress(user) == 100

# -----------------------------
# Notification Placeholder
# -----------------------------
def send_notification(email: str, message: str):
    # Replace with real email/WhatsApp integration
    print(f"Notification sent to {email}: {message}")
