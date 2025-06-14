###### ---------------hotel_booking/routes/search.py

from fastapi import APIRouter, Query
from datetime import date, timedelta
from typing import Optional
import difflib
from hotel_booking.db.json_db import load_hotels, load_rooms, load_availability

router = APIRouter()

@router.get("/search")
def search_hotels(
    q: str = "",
    guests: int = Query(1, ge=1, description="Number of guests"),
    from_date: Optional[date] = Query(None, description="Check-in date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Check-out date (YYYY-MM-DD)"),
    sort_by: str = Query("price_asc", enum=["price_asc", "price_desc", "alpha"]),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1)
):
    hotels = load_hotels()
    rooms = load_rooms()
    availability = load_availability()

    # Filter if search query provided
    if q:
        q_lower = q.lower()
        filtered = []
        for hotel in hotels:
            name = hotel.get("name", "").lower()
            city = hotel.get("city", "").lower()
            address = hotel.get("address", "").lower()
            landmark = hotel.get("landmark", "").lower()
            if q_lower in (name + city + address + landmark):
                filtered.append(hotel)
                continue
            for field in [name, city, address, landmark]:
                if difflib.get_close_matches(q_lower, [field], n=1, cutoff=0.6):
                    filtered.append(hotel)
                    break
        hotels = filtered

    results = []
    for hotel in hotels:
        # rooms matching hotel and guest capacity
        hotel_rooms = [r for r in rooms if r["hotel_id"] == hotel["id"] and r.get("capacity", 0) >= guests]
        available_rooms = []
        for room in hotel_rooms:
            if from_date and to_date:
                current = from_date
                ok = True
                while current < to_date:
                    if availability.get(room["id"], {}).get(current.isoformat()) is False:
                        ok = False
                        break
                    current += timedelta(days=1)
                if ok:
                    available_rooms.append(room)
            else:
                available_rooms.append(room)
        if not available_rooms:
            continue
        cheapest = min(available_rooms, key=lambda r: r.get("price_per_night", 0))
        entry = hotel.copy()
        entry["room"] = cheapest
        entry["price"] = cheapest.get("price_per_night", 0)
        results.append(entry)

    # Sorting
    if sort_by == "price_asc":
        results.sort(key=lambda x: x.get("price", 0))
    elif sort_by == "price_desc":
        results.sort(key=lambda x: x.get("price", 0), reverse=True)
    elif sort_by == "alpha":
        results.sort(key=lambda x: x.get("name", "").lower())

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    return results[start:end]
