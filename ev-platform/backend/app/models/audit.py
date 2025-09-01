from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class AuditEventType(str, enum.Enum):
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    KYC_REQUESTED = "kyc_requested"
    KYC_APPROVED = "kyc_approved"
    KYC_REJECTED = "kyc_rejected"
    RIDE_CREATED = "ride_created"
    RIDE_PAID = "ride_paid"
    RIDE_ASSIGNED = "ride_assigned"
    RIDE_COMPLETED = "ride_completed"
    VEHICLE_LISTED = "vehicle_listed"
    VEHICLE_APPROVED = "vehicle_approved"
    RENTAL_BOOKED = "rental_booked"
    RENTAL_RETURNED = "rental_returned"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    DEPOSIT_HELD = "deposit_held"
    DEPOSIT_RELEASED = "deposit_released"
    REWARD_ACCRUED = "reward_accrued"
    REWARD_REDEEMED = "reward_redeemed"

class Audit(Base):
    __tablename__ = "audit_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event Information
    event_type = Column(Enum(AuditEventType), nullable=False)
    event_description = Column(Text, nullable=False)
    correlation_id = Column(String, index=True)
    
    # User Context
    user_id = Column(Integer, ForeignKey("users.id"))
    admin_id = Column(Integer, ForeignKey("users.id"))
    
    # Related Entities
    ride_id = Column(Integer, ForeignKey("rides.id"))
    rental_id = Column(Integer, ForeignKey("rentals.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    payment_id = Column(Integer, ForeignKey("payments.id"))
    reward_id = Column(Integer, ForeignKey("rewards.id"))
    
    # Event Data
    old_values = Column(JSON)
    new_values = Column(JSON)
    metadata = Column(JSON)
    
    # System Information
    ip_address = Column(String)
    user_agent = Column(String)
    request_id = Column(String, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_entries", foreign_keys=[user_id])
    admin = relationship("User", foreign_keys=[admin_id])
    ride = relationship("Ride", back_populates="audit_entries")
    rental = relationship("Rental", back_populates="audit_entries")
    vehicle = relationship("Vehicle", back_populates="audit_entries")
    payment = relationship("Payment", back_populates="audit_entries")
    reward = relationship("Reward", back_populates="audit_entries")