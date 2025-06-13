###### ---------------hotel_booking/models/booking.py

from pydantic import BaseModel
from typing import Optional
from datetime import date

class Booking(BaseModel):
    id: str
    user_id: str
    room_id: str
    from_date: date
    to_date: date
    is_user_main_guest: bool
    guest_name: Optional[str] = None
    guest_family_name: Optional[str] = None
    guest_id_number: Optional[str] = None
    guest_phone: Optional[str] = None
    status: str  # e.g., "confirmed", "cancelled"
