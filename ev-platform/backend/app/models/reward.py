from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class RewardEventType(str, enum.Enum):
    RIDE_COMPLETED = "ride_completed"
    KYC_COMPLETED = "kyc_completed"
    RENTAL_ON_TIME = "rental_on_time"
    REFERRAL = "referral"
    DAILY_LOGIN = "daily_login"
    WEEKLY_ACTIVE = "weekly_active"


class RewardStatus(str, enum.Enum):
    PENDING = "pending"
    ACCRUED = "accrued"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Event Details
    event_type = Column(Enum(RewardEventType), nullable=False)
    event_id = Column(String, nullable=True)  # ID of the triggering event
    event_metadata = Column(JSON, nullable=True)  # Additional event data
    
    # Points & Status
    points_earned = Column(Integer, nullable=False)
    points_balance = Column(Integer, nullable=False)  # Running balance after this event
    status = Column(Enum(RewardStatus), default=RewardStatus.PENDING)
    
    # Rules & Caps
    rule_applied = Column(String, nullable=True)  # Which rule was triggered
    daily_cap = Column(Integer, nullable=True)  # Daily limit for this event type
    monthly_cap = Column(Integer, nullable=True)  # Monthly limit for this event type
    
    # Fraud Detection
    device_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    location = Column(String, nullable=True)
    fraud_flag = Column(Boolean, default=False)
    fraud_reason = Column(Text, nullable=True)
    
    # Redemption
    redeemed_at = Column(DateTime(timezone=True), nullable=True)
    redemption_amount = Column(Float, nullable=True)  # Value in currency
    redemption_currency = Column(String, default="inr")
    
    # Expiry
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_expired = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="rewards")
    audit_logs = relationship("AuditLog", back_populates="reward")


class RewardRule(Base):
    __tablename__ = "reward_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Rule Configuration
    event_type = Column(Enum(RewardEventType), nullable=False)
    points_per_event = Column(Integer, nullable=False)
    
    # Caps & Limits
    daily_cap = Column(Integer, nullable=True)
    weekly_cap = Column(Integer, nullable=True)
    monthly_cap = Column(Integer, nullable=True)
    
    # Conditions
    min_amount = Column(Float, nullable=True)  # Minimum transaction amount
    max_amount = Column(Float, nullable=True)  # Maximum transaction amount
    conditions = Column(JSON, nullable=True)  # Additional conditions
    
    # Status
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # Higher priority rules are applied first
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())