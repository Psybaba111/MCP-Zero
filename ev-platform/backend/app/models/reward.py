from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class RewardEventType(str, enum.Enum):
    RIDE_COMPLETED = "ride_completed"
    KYC_COMPLETED = "kyc_completed"
    RENTAL_ON_TIME = "rental_on_time"
    REFERRAL = "referral"
    DAILY_LOGIN = "daily_login"

class RewardStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Reward(Base):
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Reward Details
    event_type = Column(Enum(RewardEventType), nullable=False)
    points = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(RewardStatus), default=RewardStatus.PENDING)
    
    # Related Entities
    ride_id = Column(Integer, ForeignKey("rides.id"))
    rental_id = Column(Integer, ForeignKey("rentals.id"))
    
    # Fraud Prevention
    device_id = Column(String)
    ip_address = Column(String)
    location = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="rewards")
    ride = relationship("Ride")
    rental = relationship("Rental")
    audit_entries = relationship("AuditEntry", back_populates="reward")

class RewardBalance(Base):
    __tablename__ = "reward_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Balance Information
    total_points = Column(Integer, default=0)
    available_points = Column(Integer, default=0)
    redeemed_points = Column(Integer, default=0)
    
    # Tier Information
    current_tier = Column(String, default="bronze")
    tier_points = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")