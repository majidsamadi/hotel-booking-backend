from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from hotel_booking.routes import auth, search, booking, room, user

app = FastAPI()

# Allow CORS for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(booking.router, prefix="/bookings", tags=["Bookings"])
app.include_router(room.router, prefix="/room", tags=["Room"])
app.include_router(user.router, prefix="/users", tags=["Users"])

@app.get("/")
def root():
    return {"message": "Hotel Booking API is running."}
