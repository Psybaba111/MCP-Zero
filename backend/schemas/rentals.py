"""
Pydantic schemas for Rentals
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from database import RentalStatus

class RentalCreate(BaseModel):
    vehicle_id: uuid.UUID
    start_time: datetime
    end_time: datetime

class RentalUpdate(BaseModel):
    status: Optional[RentalStatus] = None
    return_photos: Optional[List[str]] = None
    return_notes: Optional[str] = None

class RentalResponse(BaseModel):
    id: uuid.UUID
    renter_id: uuid.UUID
    vehicle_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    hourly_rate: float
    total_amount: float
    deposit_amount: float
    status: RentalStatus
    payment_intent_id: Optional[str]
    deposit_payment_intent_id: Optional[str]
    return_photos: Optional[List[str]]
    return_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RentalReturnRequest(BaseModel):
    return_photos: Optional[List[str]] = None
    return_notes: Optional[str] = None