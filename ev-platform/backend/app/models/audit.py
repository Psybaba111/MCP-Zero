from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class AuditEventType(str, enum.Enum):
    # User Events
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    KYC_REQUESTED = "kyc_requested"
    KYC_VERIFIED = "kyc_verified"
    KYC_REJECTED = "kyc_rejected"
    
    # Ride Events
    RIDE_CREATED = "ride_created"
    RIDE_PAID = "ride_paid"
    RIDE_ASSIGNED = "ride_assigned"
    RIDE_COMPLETED = "ride_completed"
    RIDE_CANCELLED = "ride_cancelled"
    
    # Vehicle Events
    VEHICLE_LISTED = "vehicle_listed"
    VEHICLE_APPROVED = "vehicle_approved"
    VEHICLE_REJECTED = "vehicle_rejected"
    
    # Rental Events
    RENTAL_REQUESTED = "rental_requested"
    RENTAL_CONFIRMED = "rental_confirmed"
    RENTAL_STARTED = "rental_started"
    RENTAL_COMPLETED = "rental_completed"
    RENTAL_RETURNED = "rental_returned"
    
    # Payment Events
    PAYMENT_CREATED = "payment_created"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_REFUNDED = "payment_refunded"
    
    # Compliance Events
    LICENSE_EXPIRY_WARNING = "license_expiry_warning"
    SURGE_CAP_BREACH = "surge_cap_breach"
    FRAUD_DETECTED = "fraud_detected"
    
    # System Events
    AUTOMATION_TRIGGERED = "automation_triggered"
    WEBHOOK_RECEIVED = "webhook_received"
    ERROR_OCCURRED = "error_occurred"


class AuditSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Event Details
    event_type = Column(Enum(AuditEventType), nullable=False)
    event_id = Column(String, nullable=True)  # ID of the related entity
    correlation_id = Column(String, nullable=True)  # For tracking related events
    
    # User Context
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    
    # Related Entities
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=True)
    
    # Event Data
    event_data = Column(JSON, nullable=True)  # Detailed event information
    previous_state = Column(JSON, nullable=True)  # State before change
    new_state = Column(JSON, nullable=True)  # State after change
    
    # Metadata
    severity = Column(Enum(AuditSeverity), default=AuditSeverity.INFO)
    source = Column(String, nullable=True)  # API endpoint, automation, etc.
    tags = Column(JSON, nullable=True)  # Additional categorization
    
    # External Integrations
    slack_thread_ts = Column(String, nullable=True)
    notion_page_id = Column(String, nullable=True)
    pagerduty_incident_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    ride = relationship("Ride", back_populates="audit_logs")
    rental = relationship("Rental", back_populates="audit_logs")
    vehicle = relationship("Vehicle", back_populates="audit_logs")
    payment = relationship("Payment", back_populates="audit_logs")
    reward = relationship("Reward", back_populates="audit_logs")