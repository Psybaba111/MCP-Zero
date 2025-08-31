from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.payment import PaymentType, PaymentStatus, PaymentMethod


class PaymentIntentCreate(BaseModel):
    amount: int = Field(..., gt=0)  # Amount in paise
    currency: str = "inr"
    payment_type: PaymentType
    ride_id: Optional[int] = None
    rental_id: Optional[int] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PaymentIntentResponse(BaseModel):
    payment_intent_id: str
    client_secret: str
    amount: int
    currency: str
    status: PaymentStatus
    created_at: datetime
    expires_at: Optional[datetime] = None


class HyperswitchWebhook(BaseModel):
    event_type: str
    payment_intent_id: str
    status: str
    amount: int
    currency: str
    payment_method: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime


class PaymentResponse(BaseModel):
    id: int
    payment_intent_id: str
    amount: int
    currency: str
    payment_method: Optional[PaymentMethod]
    payment_type: PaymentType
    status: PaymentStatus
    ride_id: Optional[int]
    rental_id: Optional[int]
    user_id: int
    processing_at: Optional[datetime]
    succeeded_at: Optional[datetime]
    failed_at: Optional[datetime]
    error_code: Optional[str]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RefundRequest(BaseModel):
    payment_id: int
    amount: Optional[int] = None  # If None, refunds full amount
    reason: str
    metadata: Optional[Dict[str, Any]] = None


class RefundResponse(BaseModel):
    refund_id: str
    payment_id: int
    amount: int
    status: str
    reason: str
    processed_at: datetime
    message: str


class DepositHold(BaseModel):
    rental_id: int
    amount: int
    currency: str = "inr"
    description: str = "Rental deposit hold"


class DepositRelease(BaseModel):
    rental_id: int
    amount: int
    reason: str = "Rental completed successfully"
    partial_deduction: Optional[int] = None
    deduction_reason: Optional[str] = None


class PaymentMethodResponse(BaseModel):
    type: PaymentMethod
    display_name: str
    icon: str
    is_available: bool
    processing_fee: Optional[float] = None


class PaymentSummary(BaseModel):
    total_payments: int
    successful_payments: int
    failed_payments: int
    total_amount: int
    currency: str
    payment_methods: List[PaymentMethodResponse]