from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.rental import RentalStatus


class RentalRequest(BaseModel):
    vehicle_id: int
    start_time: datetime
    end_time: datetime
    pickup_location: Optional[str] = None
    return_location: Optional[str] = None


class RentalCreate(BaseModel):
    vehicle_id: int
    renter_id: int
    start_time: datetime
    end_time: datetime
    hourly_rate: float
    total_hours: float
    total_amount: float
    deposit_amount: float


class RentalResponse(BaseModel):
    id: int
    renter_id: int
    vehicle_id: int
    start_time: datetime
    end_time: datetime
    actual_return_time: Optional[datetime]
    hourly_rate: float
    total_hours: float
    total_amount: float
    deposit_amount: float
    status: RentalStatus
    confirmed_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    payment_status: str
    deposit_held: bool
    deposit_released: bool
    deposit_released_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RentalStatusUpdate(BaseModel):
    status: RentalStatus
    notes: Optional[str] = None


class RentalReturn(BaseModel):
    rental_id: int
    return_photos: List[str]
    return_odometer: float
    return_battery_percentage: float
    return_notes: Optional[str] = None
    return_location: Optional[str] = None


class RentalReturnResponse(BaseModel):
    rental_id: int
    status: RentalStatus
    deposit_release_status: str
    deposit_release_time: Optional[datetime]
    return_photos: List[str]
    return_odometer: float
    return_battery_percentage: float
    return_notes: Optional[str]
    message: str


class RentalCancellation(BaseModel):
    rental_id: int
    cancellation_reason: str
    refund_amount: Optional[float] = None


class RentalSearch(BaseModel):
    vehicle_type: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    max_price_per_hour: Optional[float] = None
    min_rating: Optional[float] = None


class RentalSummary(BaseModel):
    total_rentals: int
    active_rentals: int
    completed_rentals: int
    total_spent: float
    average_rating: Optional[float]
    upcoming_rentals: List[RentalResponse]
    past_rentals: List[RentalResponse]


class RentalOwnerView(BaseModel):
    rental: RentalResponse
    renter_details: dict
    vehicle_details: dict
    earnings: float
    deposit_status: str