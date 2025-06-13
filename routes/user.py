###### ---------------hotel_booking/routes/user.py

from fastapi import APIRouter, Depends, HTTPException
from hotel_booking.models.user import UserOut
from hotel_booking.utils.jwt_handler import decode_access_token
from hotel_booking.db.json_db import find_user_by_email, load_users
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()

auth_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = credentials.credentials
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id

@router.get("/me", response_model=UserOut)
def get_my_profile(user_id: str = Depends(get_current_user)):
    users = load_users()
    for user in users:
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "phone": user["phone"],
                "id_number": user["id_number"]
            }
    raise HTTPException(status_code=404, detail="User not found")
