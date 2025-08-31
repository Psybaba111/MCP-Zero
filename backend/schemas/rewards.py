"""
Pydantic schemas for Rewards
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class RewardEventCreate(BaseModel):
    event_type: str  # "ride_completed", "kyc_completed", "rental_on_time"
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    metadata: Optional[Dict[str, Any]] = None

class RewardEventResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    event_type: str
    points_earned: int
    entity_type: Optional[str]
    entity_id: Optional[uuid.UUID]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

class RewardAccountResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    points_balance: int
    tier: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RedemptionRequest(BaseModel):
    points: int
    redemption_type: str  # "discount", "cashback", "gift_card"
    metadata: Optional[Dict[str, Any]] = None

class RedemptionResponse(BaseModel):
    success: bool
    points_redeemed: int
    new_balance: int
    redemption_id: str