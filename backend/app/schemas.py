from datetime import date
from typing import Literal, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


DestinationId = str
Vibe = Literal["Adventure", "Cultural", "Relaxing"]
TimeSlot = Literal["Morning", "Afternoon", "Evening"]
WeatherCondition = Literal["Sunny", "Rainy", "Cloudy", "Thunderstorm"]
DisruptionType = Literal["WEATHER", "BUDGET"]


def normalize_destination_id(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "-")
    return "".join(ch for ch in normalized if ch.isalnum() or ch == "-")[:60]

class Destination(BaseModel):
    id: DestinationId
    name: str
    country: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class Activity(BaseModel):
    id: str
    destination_id: DestinationId
    name: str
    vibe: Vibe
    cost: float = Field(ge=0)
    duration_hours: float = Field(gt=0)
    is_outdoor: bool
    typical_slot: TimeSlot
    description: Optional[str] = None
    rating: float = Field(ge=0, le=5)

class Flight(BaseModel):
    id: str
    origin: str = Field(min_length=1, max_length=80)
    destination_id: DestinationId
    airline: str
    price: float = Field(ge=0)
    departure_time: str
    arrival_time: str
    direction: Literal["Outbound", "Return"]

class WeatherForecast(BaseModel):
    destination_id: DestinationId
    day_number: int = Field(ge=1, le=7)
    condition: WeatherCondition
    temp_c: int

class ItineraryPreference(BaseModel):
    origin: str = Field(min_length=1, max_length=80)
    destination_id: DestinationId = Field(min_length=1, max_length=60)
    destination_name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    vibe: Vibe
    budget: float = Field(ge=300, le=10000)
    days: int = Field(ge=3, le=7)
    start_date: date

    @field_validator("destination_id")
    @classmethod
    def normalize_destination(cls, value):
        normalized = normalize_destination_id(value)
        if not normalized:
            raise ValueError("destination_id must include letters or numbers")
        return normalized

class ItinerarySlot(BaseModel):
    time_slot: TimeSlot
    activity: Optional[Activity] = None
    cost: float = Field(ge=0)

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
    disruption_type: DisruptionType
    day_number: Optional[int] = Field(default=None, ge=1, le=7)
    weather_condition: Optional[WeatherCondition] = None
    budget_reduction_percent: Optional[float] = Field(default=None, ge=1, le=90)

    @model_validator(mode="after")
    def validate_disruption_payload(self):
        if self.disruption_type == "WEATHER" and self.day_number is None:
            raise ValueError("day_number is required for weather disruptions")
        if self.disruption_type == "BUDGET" and self.budget_reduction_percent is None:
            raise ValueError("budget_reduction_percent is required for budget disruptions")
        return self

class RecalculationResponse(BaseModel):
    itinerary: Itinerary
    decision_logs: List[str]
