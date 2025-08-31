"""
Pydantic schemas for Payments
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from database import PaymentStatus

class PaymentIntentCreate(BaseModel):
    entity_type: str  # "ride", "parcel", "rental", "deposit"
    entity_id: uuid.UUID
    amount: float

class PaymentIntentResponse(BaseModel):
    payment_intent_id: str
    client_secret: Optional[str]
    amount: float
    currency: str
    status: str

class WebhookPayload(BaseModel):
    event_type: str
    payment_intent_id: str
    status: str
    amount: Optional[int] = None
    currency: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PaymentResponse(BaseModel):
    id: uuid.UUID
    payment_intent_id: str
    user_id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    amount: float
    currency: str
    status: PaymentStatus
    hyperswitch_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RefundRequest(BaseModel):
    payment_id: uuid.UUID
    amount: Optional[float] = None  # Partial refund if specified
    reason: Optional[str] = "requested_by_customer"