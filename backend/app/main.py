from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .db import Database
from .engine import ItineraryEngine
from .schemas import (
    Destination, ItineraryPreference, Itinerary,
    DisruptionRequest, RecalculationResponse
)

app = FastAPI(
    title="Travel Planning & Experience Engine API",
    description="Backend API powering the dynamic travel itinerary generation and constraint recalculation engine.",
    version="1.0.0"
)

# Enable CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()
engine = ItineraryEngine()

@app.on_event("startup")
def startup_db():
    # Make sure database is initialized and seeded on start
    db.initialize_db()

@app.get("/api/destinations", response_model=List[Destination])
def get_destinations():
    """Lists all available mock destinations."""
    conn = db.get_connection()
    try:
        rows = conn.execute("SELECT id, name, country, description, image_url FROM destinations").fetchall()
        destinations = []
        for r in rows:
            destinations.append(Destination(
                id=r[0],
                name=r[1],
                country=r[2],
                description=r[3],
                image_url=r[4]
            ))
        return destinations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/itinerary", response_model=Itinerary)
def create_itinerary(preferences: ItineraryPreference):
    """Generates an initial day-by-day travel itinerary."""
    try:
        itinerary = engine.generate_itinerary(preferences)
        return itinerary
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/itinerary/recalculate", response_model=RecalculationResponse)
def recalculate_itinerary(request: DisruptionRequest):
    """Recalculates an itinerary based on a sudden weather alert or budget cut disruption."""
    try:
        recalculated_itin, logs = engine.recalculate_itinerary(request)
        return RecalculationResponse(
            itinerary=recalculated_itin,
            decision_logs=logs
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    """Simple API health check endpoint."""
    return {"status": "healthy", "engine": "running"}
