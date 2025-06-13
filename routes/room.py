###### ---------------hotel_booking/routes/room.py

from fastapi import APIRouter, HTTPException
from hotel_booking.models.room import Room
import json
from pathlib import Path

router = APIRouter()
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ROOMS_FILE = DATA_DIR / "rooms.json"

@router.get("/{room_id}", response_model=Room)
def get_room_details(room_id: str):
    rooms = _load_json(ROOMS_FILE)
    for room in rooms:
        if room["id"] == room_id:
            return room
    raise HTTPException(status_code=404, detail="Room not found")

def _load_json(path: Path):
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)
