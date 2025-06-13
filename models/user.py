###### ---------------hotel_booking/models/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    first_name: str
    last_name: str
    phone: str
    id_number: str

class UserLogin(UserBase):
    password: str
    remember_me: Optional[bool] = False

class UserOut(UserBase):
    id: str
    first_name: str
    last_name: str
    phone: str
    id_number: str

class UserInDB(UserBase):
    id: Optional[str] = None
    first_name: str
    last_name: str
    phone: str
    id_number: str
    hashed_password: str
