###### ---------------hotel_booking/routes/booking.py

from fastapi import APIRouter, HTTPException, Depends, status
from hotel_booking.models.booking import Booking
from uuid import uuid4
from datetime import date, timedelta
from pydantic import BaseModel, model_validator
from hotel_booking.db.json_db import (
    load_rooms,
    load_hotels,
    load_availability,
    save_availability,
    save_booking,
    load_bookings,
    save_bookings_list
)
from hotel_booking.dependencies import get_current_user, get_user_object

router = APIRouter()

class BookingRequest(BaseModel):
    room_id: str
    from_date: date
    to_date: date
    is_user_main_guest: bool
    guest_name: str | None = None
    guest_family_name: str | None = None
    guest_id_number: str | None = None
    guest_phone: str | None = None

    @model_validator(mode='after')
    def validate_dates_and_guests(self) -> 'BookingRequest':
        if self.from_date < date.today() or self.to_date <= self.from_date:
            raise ValueError("Invalid booking dates. Ensure 'from_date' is today or later and before 'to_date'.")
        if not self.is_user_main_guest:
            missing = [
                field for field in ["guest_name", "guest_family_name", "guest_id_number", "guest_phone"]
                if not getattr(self, field)
            ]
            if missing:
                raise ValueError(f"Missing guest fields: {', '.join(missing)}")
        return self

@router.post("/", response_model=Booking)
def book_room(req: BookingRequest, user_id: str = Depends(get_current_user)):
    user = get_user_object(user_id)
    # prepare guest info
    if req.is_user_main_guest:
        guest_info = {
            "guest_name": user["first_name"],
            "guest_family_name": user["last_name"],
            "guest_id_number": user["id_number"],
            "guest_phone": user["phone"],
        }
    else:
        guest_info = req.model_dump(include={"guest_name","guest_family_name","guest_id_number","guest_phone"})

    # check availability
    availability = load_availability()
    current = req.from_date
    while current < req.to_date:
        if availability.get(req.room_id, {}).get(current.isoformat()) is False:
            raise HTTPException(status_code=400, detail="Room not available for the selected dates")
        current += timedelta(days=1)

    # create booking
    booking = Booking(
        id=str(uuid4()),
        user_id=user_id,
        room_id=req.room_id,
        from_date=req.from_date,
        to_date=req.to_date,
        is_user_main_guest=req.is_user_main_guest,
        status="confirmed",
        **guest_info
    )
    # mark unavailable
    availability.setdefault(req.room_id, {})
    current = req.from_date
    while current < req.to_date:
        availability[req.room_id][current.isoformat()] = False
        current += timedelta(days=1)
    save_availability(availability)

    # persist booking
    save_booking(booking.model_dump())
    return booking

@router.get("/me", response_model=list[dict])
def get_all_bookings(user_id: str = Depends(get_current_user)):
    return _get_enriched_bookings(user_id)

@router.get("/me/upcoming", response_model=list[dict])
def get_upcoming_bookings(user_id: str = Depends(get_current_user)):
    today = date.today()
    return _get_enriched_bookings(user_id, upcoming_only=True, today=today)

@router.post("/{booking_id}/cancel", response_model=dict)
def cancel_booking(booking_id: str, user_id: str = Depends(get_current_user)):
    bookings = load_bookings()
    updated = False
    cancelled_booking = None
    for b in bookings:
        if b["id"] == booking_id and b["user_id"] == user_id:
            b["status"] = "cancelled"
            cancelled_booking = b
            # release availability
            availability = load_availability()
            current = date.fromisoformat(b["from_date"])
            end = date.fromisoformat(b["to_date"])
            while current < end:
                availability.setdefault(b["room_id"], {})[current.isoformat()] = True
                current += timedelta(days=1)
            save_availability(availability)
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail="Booking not found or not owned by user")
    save_bookings_list(bookings)
    return {"detail": "Booking cancelled successfully", "booking": cancelled_booking}


def _get_enriched_bookings(user_id: str, upcoming_only: bool = False, today: date = None) -> list[dict]:
    bookings = [b for b in load_bookings() if b["user_id"] == user_id]
    if upcoming_only:
        bookings = [b for b in bookings if b.get("status") == "confirmed" and date.fromisoformat(b["to_date"]) >= today]
    rooms = {r["id"]: r for r in load_rooms()}
    hotels = {h["id"]: h for h in load_hotels()}
    enriched = []
    for b in bookings:
        room = rooms.get(b["room_id"])
        hotel = hotels.get(room["hotel_id"]) if room else None
        enriched.append({
            "reservationInfo": b,
            "roomInfo": room,
            "hotelInfo": hotel
        })
    return enriched
