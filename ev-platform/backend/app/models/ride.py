from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class RideType(str, enum.Enum):
    RIDE = "ride"
    PARCEL = "parcel"


class RideStatus(str, enum.Enum):
    CREATED = "created"
    PAID = "paid"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    ride_type = Column(Enum(RideType), nullable=False)
    
    # Users
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Location & Route
    pickup_location = Column(Text, nullable=False)
    pickup_latitude = Column(Float, nullable=True)
    pickup_longitude = Column(Float, nullable=True)
    
    drop_location = Column(Text, nullable=False)
    drop_latitude = Column(Float, nullable=True)
    drop_longitude = Column(Float, nullable=True)
    
    # Vehicle & Pricing
    vehicle_type_preference = Column(String, nullable=True)
    estimated_distance = Column(Float, nullable=True)  # km
    estimated_duration = Column(Integer, nullable=True)  # minutes
    base_fare = Column(Float, nullable=False)
    distance_fare = Column(Float, nullable=True)
    time_fare = Column(Float, nullable=True)
    surge_multiplier = Column(Float, default=1.0)
    total_fare = Column(Float, nullable=False)
    
    # Parcel Details (if ride_type == PARCEL)
    parcel_weight = Column(Float, nullable=True)  # kg
    parcel_dimensions = Column(String, nullable=True)  # LxWxH cm
    parcel_description = Column(Text, nullable=True)
    parcel_fragile = Column(Boolean, default=False)
    
    # Status & Timing
    status = Column(Enum(RideStatus), default=RideStatus.CREATED)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    picked_up_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Payment
    payment_intent_id = Column(String, nullable=True)
    payment_status = Column(String, default="pending")
    payment_method = Column(String, nullable=True)
    
    # Driver Assignment
    driver_rating = Column(Float, nullable=True)
    passenger_rating = Column(Float, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    passenger = relationship("User", back_populates="rides", foreign_keys=[passenger_id])
    driver = relationship("User", foreign_keys=[driver_id])
    audit_logs = relationship("AuditLog", back_populates="ride")
    payments = relationship("Payment", back_populates="ride")