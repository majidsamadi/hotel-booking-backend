###### ---------------hotel_booking/models/room.py

from pydantic import BaseModel
from typing import List

class Room(BaseModel):
    id: str
    hotel_id: str
    room_type: str  # deluxe, vip, normal
    price_per_night: float
    capacity: int
    beds: str  # e.g., "1 king bed and 1 queen bed"
    description: str
    amenities: List[str]
    images: List[str]
