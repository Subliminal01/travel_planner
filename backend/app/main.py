import logging
import os
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .db import Database
from .engine import ItineraryEngine
from .schemas import (
    Destination, ItineraryPreference, Itinerary,
    DisruptionRequest, RecalculationResponse
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Travel Planning & Experience Engine API",
    description="Backend API powering the dynamic travel itinerary generation and constraint recalculation engine.",
    version="1.0.0"
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
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
        return [
            Destination(
                id=r[0],
                name=r[1],
                country=r[2],
                description=r[3],
                image_url=r[4]
            )
            for r in rows
        ]
    except Exception:
        logger.exception("Failed to list destinations")
        raise HTTPException(status_code=500, detail="Failed to list destinations")
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
    except Exception:
        logger.exception("Failed to generate itinerary")
        raise HTTPException(status_code=500, detail="Failed to generate itinerary")

@app.post("/api/itinerary/recalculate", response_model=RecalculationResponse)
def recalculate_itinerary(request: DisruptionRequest):
    """Recalculates an itinerary based on a sudden weather alert or budget cut disruption."""
    try:
        recalculated_itin, logs = engine.recalculate_itinerary(request)
        return RecalculationResponse(
            itinerary=recalculated_itin,
            decision_logs=logs
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        logger.exception("Failed to recalculate itinerary")
        raise HTTPException(status_code=500, detail="Failed to recalculate itinerary")

@app.get("/api/health")
def health_check():
    """Simple API health check endpoint."""
    return {"status": "healthy", "engine": "running"}
