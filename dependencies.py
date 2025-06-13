###### ---------------hotel_booking/dependencies.py

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from hotel_booking.utils.jwt_handler import decode_access_token
from hotel_booking.db.json_db import find_user_by_email, load_users

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return user_id

def get_user_object(user_id: str):
    users = load_users()
    for user in users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

def find_user_by_id(user_id: str):
    users = load_users()
    for user in users:
        if user["id"] == user_id:
            return user
    return None
