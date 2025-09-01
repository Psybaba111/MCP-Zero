from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..models.ride import RideStatus, RideType

# Base Ride Schema
class RideBase(BaseModel):
    pickup_address: str = Field(..., min_length=5)
    pickup_latitude: float = Field(..., ge=-90, le=90)
    pickup_longitude: float = Field(..., ge=-180, le=180)
    drop_address: str = Field(..., min_length=5)
    drop_latitude: float = Field(..., ge=-90, le=90)
    drop_longitude: float = Field(..., ge=-180, le=180)
    type: RideType = RideType.RIDE

# Ride Create Schema
class RideCreate(RideBase):
    pass

# Parcel Create Schema
class ParcelCreate(RideBase):
    type: RideType = RideType.PARCEL
    parcel_description: str = Field(..., min_length=5)
    parcel_weight: float = Field(..., gt=0)
    parcel_dimensions: str = Field(..., min_length=3)

# Ride Response Schema
class RideResponse(RideBase):
    id: int
    user_id: int
    driver_id: Optional[int] = None
    status: RideStatus
    payment_status: str
    payment_intent_id: Optional[str] = None
    base_fare: float
    distance_fare: Optional[float] = None
    time_fare: Optional[float] = None
    total_fare: float
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Ride Update Schema
class RideUpdate(BaseModel):
    status: Optional[RideStatus] = None
    driver_id: Optional[int] = None
    payment_status: Optional[str] = None
    payment_intent_id: Optional[str] = None

# Ride Estimate Schema
class RideEstimate(BaseModel):
    pickup_address: str
    drop_address: str
    type: RideType = RideType.RIDE
    parcel_weight: Optional[float] = None

# Ride Estimate Response Schema
class RideEstimateResponse(BaseModel):
    base_fare: float
    distance_fare: float
    time_fare: float
    total_fare: float
    estimated_duration: int  # minutes
    estimated_distance: float  # km