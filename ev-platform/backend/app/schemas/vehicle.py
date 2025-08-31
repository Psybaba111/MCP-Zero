from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.vehicle import VehicleType, VehicleStatus


class VehicleBase(BaseModel):
    vehicle_type: VehicleType
    brand: str = Field(..., min_length=2, max_length=50)
    model: str = Field(..., min_length=2, max_length=50)
    year: int = Field(..., ge=1900, le=2030)
    color: str = Field(..., min_length=2, max_length=30)
    battery_capacity: Optional[float] = None
    range_km: Optional[float] = None
    max_speed: Optional[float] = None
    seating_capacity: Optional[int] = None


class VehicleCreate(VehicleBase):
    hourly_rate: float = Field(..., gt=0)
    daily_rate: float = Field(..., gt=0)
    deposit_amount: float = Field(..., gt=0)
    pickup_location: str = Field(..., min_length=5)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    registration_number: str = Field(..., min_length=5, max_length=20)
    insurance_number: Optional[str] = None
    fitness_certificate: Optional[str] = None
    puc_certificate: Optional[str] = None
    photos: Optional[List[str]] = []
    documents: Optional[List[str]] = []


class VehicleUpdate(BaseModel):
    hourly_rate: Optional[float] = Field(None, gt=0)
    daily_rate: Optional[float] = Field(None, gt=0)
    deposit_amount: Optional[float] = Field(None, gt=0)
    pickup_location: Optional[str] = Field(None, min_length=5)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: Optional[List[str]] = []
    documents: Optional[List[str]] = []
    status: Optional[VehicleStatus] = None


class VehicleResponse(VehicleBase):
    id: int
    owner_id: int
    hourly_rate: float
    daily_rate: float
    deposit_amount: float
    pickup_location: str
    latitude: Optional[float]
    longitude: Optional[float]
    registration_number: str
    insurance_number: Optional[str]
    fitness_certificate: Optional[str]
    puc_certificate: Optional[str]
    status: VehicleStatus
    approval_notes: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    photos: Optional[List[str]]
    documents: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class VehicleApproval(BaseModel):
    status: VehicleStatus
    approval_notes: Optional[str] = None
    approved_by: int


class VehicleSearch(BaseModel):
    vehicle_type: Optional[VehicleType] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = 10.0
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    max_distance: Optional[float] = None


class VehicleAvailability(BaseModel):
    vehicle_id: int
    available_slots: List[dict]  # List of available time slots
    next_available: Optional[datetime] = None
    is_available_now: bool


class VehicleOwnerResponse(BaseModel):
    vehicle: VehicleResponse
    total_earnings: float
    total_rentals: int
    average_rating: Optional[float]
    upcoming_bookings: List[dict]