"""
Pydantic schemas for Rides and Parcels
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from database import RideStatus, VehicleType

class RideCreate(BaseModel):
    pickup_lat: float
    pickup_lng: float
    pickup_address: str
    drop_lat: float
    drop_lng: float
    drop_address: str
    vehicle_type: VehicleType

class RideUpdate(BaseModel):
    status: Optional[RideStatus] = None
    driver_id: Optional[uuid.UUID] = None
    final_fare: Optional[float] = None

class RideResponse(BaseModel):
    id: uuid.UUID
    passenger_id: uuid.UUID
    driver_id: Optional[uuid.UUID]
    pickup_lat: float
    pickup_lng: float
    pickup_address: str
    drop_lat: float
    drop_lng: float
    drop_address: str
    vehicle_type: VehicleType
    estimated_fare: Optional[float]
    final_fare: Optional[float]
    status: RideStatus
    payment_intent_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ParcelCreate(BaseModel):
    pickup_lat: float
    pickup_lng: float
    pickup_address: str
    drop_lat: float
    drop_lng: float
    drop_address: str
    recipient_name: str
    recipient_phone: str
    weight_kg: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None  # {length, width, height}

class ParcelUpdate(BaseModel):
    status: Optional[RideStatus] = None
    driver_id: Optional[uuid.UUID] = None
    final_fare: Optional[float] = None

class ParcelResponse(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    driver_id: Optional[uuid.UUID]
    pickup_lat: float
    pickup_lng: float
    pickup_address: str
    drop_lat: float
    drop_lng: float
    drop_address: str
    recipient_name: str
    recipient_phone: str
    weight_kg: Optional[float]
    dimensions: Optional[Dict[str, float]]
    estimated_fare: Optional[float]
    final_fare: Optional[float]
    status: RideStatus
    payment_intent_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True