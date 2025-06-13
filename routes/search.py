###### ---------------hotel_booking/routes/search.py

from fastapi import APIRouter, Query
from datetime import date
from hotel_booking.db.json_db import load_hotels, load_rooms, load_availability
import difflib

router = APIRouter()

@router.get("/search")
def search_hotels(
    q: str = "",
    sort_by: str = Query("price_asc", enum=["price_asc", "price_desc", "alpha"]),
    page: int = 1,
    per_page: int = 10,
    from_date: date | None = None,
    to_date: date | None = None,
):
    hotels = load_hotels()
    rooms = load_rooms()
    availability = load_availability()

    # Filter only if search query is provided
    if q:
        q_lower = q.lower()
        matched_hotels = []
        for hotel in hotels:
            name = hotel.get("name", "").lower()
            city = hotel.get("city", "").lower()
            address = hotel.get("address", "").lower()
            landmark = hotel.get("landmark", "").lower()

            if q_lower in name or q_lower in city or q_lower in address or q_lower in landmark:
                matched_hotels.append(hotel)
                continue

            fields = [name, city, address, landmark]
            for field in fields:
                if difflib.get_close_matches(q_lower, [field], n=1, cutoff=0.6):
                    matched_hotels.append(hotel)
                    break
        hotels = matched_hotels

    # Attach one available room with lowest price
    results = []
    for hotel in hotels:
        hotel_rooms = [room for room in rooms if room["hotel_id"] == hotel["id"]]
        available_rooms = []
        for room in hotel_rooms:
            if from_date and to_date:
                is_available = True
                current = from_date
                while current < to_date:
                    if availability.get(room["id"], {}).get(current.isoformat()) is False:
                        is_available = False
                        break
                    current = current.replace(day=current.day + 1)
                if is_available:
                    available_rooms.append(room)
            else:
                available_rooms.append(room)

        if available_rooms:
            cheapest_room = min(available_rooms, key=lambda r: r["price_per_night"])
            hotel_copy = hotel.copy()
            hotel_copy["room"] = cheapest_room
            hotel_copy["price"] = cheapest_room["price_per_night"]
            results.append(hotel_copy)

    if sort_by == "price_asc":
        results.sort(key=lambda h: h["price"])
    elif sort_by == "price_desc":
        results.sort(key=lambda h: h["price"], reverse=True)
    elif sort_by == "alpha":
        results.sort(key=lambda h: h["name"].lower())

    start = (page - 1) * per_page
    end = start + per_page
    return results[start:end]
