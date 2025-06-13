###### ---------------hotel_booking/routes/auth.py

from fastapi import APIRouter, HTTPException
from hotel_booking.models.user import UserCreate, UserLogin, UserOut, UserInDB
from hotel_booking.utils.jwt_handler import create_access_token
from hotel_booking.utils.auth import hash_password, verify_password
from hotel_booking.db.json_db import save_user, find_user_by_email
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate):
    existing_user = find_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    user_db = UserInDB(
        **user.dict(exclude={"password"}),
        hashed_password=hashed_pw
    )
    saved_user_dict = save_user(user_db)
    return UserOut(**saved_user_dict)

@router.post("/login")
def login(user: UserLogin):
    db_user = find_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expires = timedelta(days=365) if user.remember_me else timedelta(minutes=15)
    token = create_access_token(db_user["id"], expires_delta=expires)
    return {"access_token": token, "token_type": "bearer"}
