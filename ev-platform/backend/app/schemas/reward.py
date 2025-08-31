from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.reward import RewardEventType, RewardStatus


class RewardEvent(BaseModel):
    event_type: RewardEventType
    event_id: Optional[str] = None
    event_metadata: Optional[Dict[str, Any]] = None
    user_id: int
    points_earned: int
    rule_applied: Optional[str] = None


class RewardResponse(BaseModel):
    id: int
    user_id: int
    event_type: RewardEventType
    event_id: Optional[str]
    event_metadata: Optional[Dict[str, Any]]
    points_earned: int
    points_balance: int
    status: RewardStatus
    rule_applied: Optional[str]
    daily_cap: Optional[int]
    monthly_cap: Optional[int]
    fraud_flag: bool
    fraud_reason: Optional[str]
    redeemed_at: Optional[datetime]
    redemption_amount: Optional[float]
    redemption_currency: str
    expires_at: Optional[datetime]
    is_expired: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RewardBalance(BaseModel):
    user_id: int
    total_points: int
    available_points: int
    expired_points: int
    tier: str
    next_tier: Optional[str]
    points_to_next_tier: Optional[int]
    tier_benefits: List[str]


class RewardRedemption(BaseModel):
    points_to_redeem: int = Field(..., gt=0)
    redemption_type: str  # "cashback", "discount", "voucher"
    redemption_value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class RewardRedemptionResponse(BaseModel):
    redemption_id: str
    points_redeemed: int
    redemption_type: str
    redemption_value: float
    currency: str
    status: str
    processed_at: datetime
    message: str


class RewardRule(BaseModel):
    event_type: RewardEventType
    points_per_event: int
    daily_cap: Optional[int] = None
    weekly_cap: Optional[int] = None
    monthly_cap: Optional[int] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    conditions: Optional[Dict[str, Any]] = None
    is_active: bool = True
    priority: int = 1


class RewardRuleResponse(RewardRule):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RewardHistory(BaseModel):
    user_id: int
    total_events: int
    total_points_earned: int
    total_points_redeemed: int
    events: List[RewardResponse]
    redemptions: List[RewardRedemptionResponse]


class RewardTier(BaseModel):
    tier_name: str
    min_points: int
    max_points: Optional[int]
    benefits: List[str]
    icon: str
    color: str


class RewardLeaderboard(BaseModel):
    user_id: int
    user_name: str
    total_points: int
    tier: str
    rank: int
    monthly_points: int
    weekly_points: int