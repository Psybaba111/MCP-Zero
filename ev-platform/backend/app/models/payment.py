from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class PaymentType(str, enum.Enum):
    RIDE = "ride"
    RENTAL = "rental"
    DEPOSIT = "deposit"
    REFUND = "refund"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Payment Details
    payment_intent_id = Column(String, unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    type = Column(Enum(PaymentType), nullable=False)
    
    # Hyperswitch Integration
    hyperswitch_payment_id = Column(String, unique=True, index=True)
    hyperswitch_refund_id = Column(String, unique=True, index=True)
    payment_method = Column(String)  # UPI, card, etc.
    
    # Related Entities
    ride_id = Column(Integer, ForeignKey("rides.id"))
    rental_id = Column(Integer, ForeignKey("rentals.id"))
    
    # Webhook Data
    webhook_received = Column(Boolean, default=False)
    webhook_data = Column(Text)  # JSON string of webhook payload
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")
    ride = relationship("Ride")
    rental = relationship("Rental")
    audit_entries = relationship("AuditEntry", back_populates="payment")