from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class RentalStatus(str, enum.Enum):
    BOOKED = "booked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class Rental(Base):
    __tablename__ = "rentals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    
    # Booking Details
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    pickup_location = Column(Text, nullable=False)
    return_location = Column(Text, nullable=False)
    
    # Pricing
    hourly_rate = Column(Float, nullable=False)
    total_hours = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    deposit_amount = Column(Float, nullable=False)
    
    # Status and Tracking
    status = Column(Enum(RentalStatus), default=RentalStatus.BOOKED)
    payment_status = Column(String, default="pending")
    payment_intent_id = Column(String, unique=True, index=True)
    
    # Return Details
    returned_at = Column(DateTime(timezone=True))
    return_photos = Column(Text)  # JSON array of photo URLs
    return_odometer = Column(Float)
    return_battery_percentage = Column(Float)
    return_notes = Column(Text)
    
    # Deposit Management
    deposit_held = Column(Boolean, default=False)
    deposit_released = Column(Boolean, default=False)
    deposit_released_at = Column(DateTime(timezone=True))
    deposit_deductions = Column(Float, default=0.0)
    deduction_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="rentals")
    vehicle = relationship("Vehicle", back_populates="rentals")
    audit_entries = relationship("AuditEntry", back_populates="rental")