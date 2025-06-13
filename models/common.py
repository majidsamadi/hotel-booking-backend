###### ---------------hotel_booking/models/common.py

from pydantic import BaseModel
from datetime import date

class DateRangeQuery(BaseModel):
    from_date: date
    to_date: date

class RoomSearchQuery(DateRangeQuery):
    query: str  # hotel name / city / landmark
    guests: int
