###### ---------------hotel_booking/db/json_db.py

import json
import os
from uuid import uuid4
from datetime import date, datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def read_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def write_json(filename, data):
    path = os.path.join(DATA_DIR, filename)

    def default_serializer(obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        raise TypeError(f"Type {obj.__class__.__name__} not serializable")

    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=default_serializer)


def load_users():
    return read_json("users.json")


def save_users(users):
    write_json("users.json", users)


def save_user(user):
    users = load_users()
    user_dict = user.model_dump()
    user_dict["id"] = str(uuid4())
    users.append(user_dict)
    save_users(users)
    return user_dict



def find_user_by_email(email):
    users = load_users()
    for user in users:
        if user.get("email") == email:
            return user
    return None


def load_hotels():
    return read_json("hotels.json")


def load_rooms():
    return read_json("rooms.json")


def load_availability():
    path = os.path.join(DATA_DIR, "availability.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_availability(availability):
    write_json("availability.json", availability)


def load_bookings():
    return read_json("bookings.json")


def save_booking(booking):
    bookings = load_bookings()
    booking["id"] = str(uuid4())
    bookings.append(booking)
    write_json("bookings.json", bookings)
