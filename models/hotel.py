###### ---------------hotel_booking/models/hotel.py

from pydantic import BaseModel
from typing import List

class Hotel(BaseModel):
    id: str
    name: str
    city: str
    address: str
    description: str
    landmark: str
