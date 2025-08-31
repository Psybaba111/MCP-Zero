from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class RentalStatus(str, enum.Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    
    # Users & Vehicle
    renter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    
    # Timing
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    actual_return_time = Column(DateTime(timezone=True), nullable=True)
    
    # Pricing
    hourly_rate = Column(Float, nullable=False)
    total_hours = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    deposit_amount = Column(Float, nullable=False)
    
    # Status & Lifecycle
    status = Column(Enum(RentalStatus), default=RentalStatus.REQUESTED)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Payment
    payment_intent_id = Column(String, nullable=True)
    payment_status = Column(String, default="pending")
    deposit_held = Column(Boolean, default=False)
    deposit_released = Column(Boolean, default=False)
    deposit_released_at = Column(DateTime(timezone=True), nullable=True)
    
    # Return & Inspection
    return_photos = Column(Text, nullable=True)  # JSON array of photo URLs
    return_odometer = Column(Float, nullable=True)  # km
    return_battery_percentage = Column(Float, nullable=True)
    return_notes = Column(Text, nullable=True)
    
    # Cancellation & Refunds
    cancellation_reason = Column(Text, nullable=True)
    refund_amount = Column(Float, nullable=True)
    refund_processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    renter = relationship("User", back_populates="rentals", foreign_keys=[renter_id])
    vehicle = relationship("Vehicle", back_populates="rentals")
    audit_logs = relationship("AuditLog", back_populates="rental")
    payments = relationship("Payment", back_populates="rental")