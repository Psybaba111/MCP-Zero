from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.ride import RideType, RideStatus


class LocationRequest(BaseModel):
    pickup_location: str = Field(..., min_length=5)
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    drop_location: str = Field(..., min_length=5)
    drop_latitude: Optional[float] = None
    drop_longitude: Optional[float] = None


class RideRequest(LocationRequest):
    ride_type: RideType = RideType.RIDE
    vehicle_type_preference: Optional[str] = None
    parcel_weight: Optional[float] = None
    parcel_dimensions: Optional[str] = None
    parcel_description: Optional[str] = None
    parcel_fragile: bool = False


class RideEstimate(BaseModel):
    estimated_distance: float  # km
    estimated_duration: int  # minutes
    base_fare: float
    distance_fare: float
    time_fare: float
    surge_multiplier: float
    total_fare: float
    currency: str = "INR"


class RideCreate(BaseModel):
    ride_type: RideType
    pickup_location: str
    pickup_latitude: Optional[float]
    pickup_longitude: Optional[float]
    drop_location: str
    drop_latitude: Optional[float]
    drop_longitude: Optional[float]
    vehicle_type_preference: Optional[str]
    estimated_distance: Optional[float]
    estimated_duration: Optional[int]
    base_fare: float
    distance_fare: Optional[float]
    time_fare: Optional[float]
    surge_multiplier: float = 1.0
    total_fare: float
    parcel_weight: Optional[float] = None
    parcel_dimensions: Optional[str] = None
    parcel_description: Optional[str] = None
    parcel_fragile: bool = False


class RideResponse(BaseModel):
    id: int
    ride_type: RideType
    passenger_id: int
    driver_id: Optional[int]
    pickup_location: str
    drop_location: str
    estimated_distance: Optional[float]
    estimated_duration: Optional[int]
    total_fare: float
    status: RideStatus
    requested_at: datetime
    assigned_at: Optional[datetime]
    picked_up_at: Optional[datetime]
    completed_at: Optional[datetime]
    payment_status: str
    parcel_weight: Optional[float]
    parcel_dimensions: Optional[str]
    parcel_fragile: bool

    class Config:
        from_attributes = True


class RideStatusUpdate(BaseModel):
    status: RideStatus
    driver_id: Optional[int] = None
    notes: Optional[str] = None


class DriverAssignment(BaseModel):
    driver_id: int
    estimated_arrival: int  # minutes
    driver_name: str
    driver_phone: str
    vehicle_details: str


class RideTracking(BaseModel):
    ride_id: int
    status: RideStatus
    driver_location: Optional[dict] = None
    estimated_arrival: Optional[int] = None
    current_location: Optional[dict] = None
    last_updated: datetime


class ParcelDetails(BaseModel):
    weight: float
    dimensions: str
    description: str
    fragile: bool
    pickup_instructions: Optional[str] = None
    delivery_instructions: Optional[str] = None