"""
Pydantic schemas for Vehicles
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from database import VehicleType, VehicleStatus

class VehicleCreate(BaseModel):
    vehicle_type: VehicleType
    make: str
    model: str
    year: Optional[int] = None
    registration_number: str
    battery_capacity: Optional[float] = None  # kWh
    range_km: Optional[float] = None
    hourly_rate: float
    daily_rate: float
    deposit_amount: float
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    photos: Optional[List[str]] = None  # URLs
    features: Optional[List[str]] = None

class VehicleUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    battery_capacity: Optional[float] = None
    range_km: Optional[float] = None
    hourly_rate: Optional[float] = None
    daily_rate: Optional[float] = None
    deposit_amount: Optional[float] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    photos: Optional[List[str]] = None
    features: Optional[List[str]] = None
    status: Optional[VehicleStatus] = None

class VehicleResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    vehicle_type: VehicleType
    make: str
    model: str
    year: Optional[int]
    registration_number: str
    battery_capacity: Optional[float]
    range_km: Optional[float]
    hourly_rate: float
    daily_rate: float
    deposit_amount: float
    status: VehicleStatus
    location_lat: Optional[float]
    location_lng: Optional[float]
    photos: Optional[List[str]]
    features: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VehicleSearchFilters(BaseModel):
    vehicle_type: Optional[VehicleType] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: Optional[float] = 10
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    available_only: bool = True