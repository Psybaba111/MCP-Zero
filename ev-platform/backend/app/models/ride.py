from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class RideStatus(str, enum.Enum):
    CREATED = "created"
    PAID = "paid"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RideType(str, enum.Enum):
    RIDE = "ride"
    PARCEL = "parcel"

class Ride(Base):
    __tablename__ = "rides"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"))
    
    # Ride Details
    type = Column(Enum(RideType), default=RideType.RIDE)
    pickup_address = Column(Text, nullable=False)
    pickup_latitude = Column(Float, nullable=False)
    pickup_longitude = Column(Float, nullable=False)
    drop_address = Column(Text, nullable=False)
    drop_latitude = Column(Float, nullable=False)
    drop_longitude = Column(Float, nullable=False)
    
    # Parcel Details (if type is parcel)
    parcel_description = Column(Text)
    parcel_weight = Column(Float)
    parcel_dimensions = Column(String)
    
    # Pricing
    base_fare = Column(Float, nullable=False)
    distance_fare = Column(Float)
    time_fare = Column(Float)
    total_fare = Column(Float, nullable=False)
    
    # Status and Tracking
    status = Column(Enum(RideStatus), default=RideStatus.CREATED)
    payment_status = Column(String, default="pending")
    payment_intent_id = Column(String, unique=True, index=True)
    
    # Driver Assignment
    assigned_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="rides", foreign_keys=[user_id])
    driver = relationship("User", foreign_keys=[driver_id])
    audit_entries = relationship("AuditEntry", back_populates="ride")