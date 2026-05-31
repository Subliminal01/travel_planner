from pydantic import BaseModel
from typing import List, Optional

class Destination(BaseModel):
    id: str
    name: str
    country: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class Activity(BaseModel):
    id: str
    destination_id: str
    name: str
    vibe: str  # 'Adventure', 'Cultural', 'Relaxing'
    cost: float
    duration_hours: float
    is_outdoor: bool
    typical_slot: str  # 'Morning', 'Afternoon', 'Evening'
    description: Optional[str] = None
    rating: float

class Flight(BaseModel):
    id: str
    origin: str
    destination_id: str
    airline: str
    price: float
    departure_time: str
    arrival_time: str
    direction: str  # 'Outbound' or 'Return'

class WeatherForecast(BaseModel):
    destination_id: str
    day_number: int
    condition: str  # 'Sunny', 'Rainy', 'Cloudy', 'Thunderstorm'
    temp_c: int

class ItineraryPreference(BaseModel):
    origin: str
    destination_id: str
    vibe: str  # 'Adventure', 'Cultural', 'Relaxing'
    budget: float
    days: int
    start_date: str

class ItinerarySlot(BaseModel):
    time_slot: str  # 'Morning', 'Afternoon', 'Evening'
    activity: Optional[Activity] = None
    cost: float

class ItineraryDay(BaseModel):
    day_number: int
    weather: WeatherForecast
    slots: List[ItinerarySlot]

class Itinerary(BaseModel):
    preferences: ItineraryPreference
    outbound_flight: Flight
    return_flight: Flight
    days: List[ItineraryDay]
    total_cost: float
    budget_remaining: float

class DisruptionRequest(BaseModel):
    preferences: ItineraryPreference
    current_itinerary: Itinerary
    disruption_type: str  # 'WEATHER' or 'BUDGET'
    day_number: Optional[int] = None
    weather_condition: Optional[str] = None
    budget_reduction_percent: Optional[float] = None

class RecalculationResponse(BaseModel):
    itinerary: Itinerary
    decision_logs: List[str]
