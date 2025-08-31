from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class PaymentType(str, enum.Enum):
    RIDE = "ride"
    RENTAL = "rental"
    DEPOSIT = "deposit"
    REFUND = "refund"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    UPI = "upi"
    CARD = "card"
    NETBANKING = "netbanking"
    WALLET = "wallet"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Hyperswitch Integration
    payment_intent_id = Column(String, unique=True, nullable=False)
    client_secret = Column(String, nullable=True)
    
    # Payment Details
    amount = Column(Float, nullable=False)  # in paise
    currency = Column(String, default="inr")
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    payment_type = Column(Enum(PaymentType), nullable=False)
    
    # Status & Lifecycle
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    processing_at = Column(DateTime(timezone=True), nullable=True)
    succeeded_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Related Entities
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Hyperswitch Response
    hyperswitch_response = Column(JSON, nullable=True)
    error_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Refund Details
    refund_amount = Column(Float, nullable=True)
    refund_reason = Column(Text, nullable=True)
    refund_processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    ride = relationship("Ride", back_populates="payments")
    rental = relationship("Rental", back_populates="payments")
    audit_logs = relationship("AuditLog", back_populates="payment")