###### ---------------hotel_booking/routes/user.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from hotel_booking.models.user import UserOut
from hotel_booking.utils.jwt_handler import decode_access_token
from hotel_booking.db.json_db import load_users, save_users

router = APIRouter()

auth_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = credentials.credentials
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    id_number: str | None = None


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


@router.put("/me", response_model=UserOut)
def update_profile(
    payload: UserUpdate,
    user_id: str = Depends(get_current_user)
):
    users = load_users()
    updated_user = None
    for u in users:
        if u["id"] == user_id:
            for field, value in payload.model_dump().items():
                if value is not None:
                    u[field] = value
            updated_user = u
            break
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    save_users(users)
    return updated_user
