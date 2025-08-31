from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class VehicleType(str, enum.Enum):
    CAR = "car"
    BIKE = "bike"
    SCOOTER = "scooter"
    CYCLE = "cycle"

class VehicleStatus(str, enum.Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    INACTIVE = "inactive"

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic Information
    type = Column(Enum(VehicleType), nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    
    # Technical Details
    battery_capacity = Column(Float)  # kWh
    range_km = Column(Float)
    max_speed = Column(Float)
    seating_capacity = Column(Integer)
    
    # Location and Availability
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(Text)
    city = Column(String)
    
    # Pricing
    hourly_rate = Column(Float, nullable=False)
    daily_rate = Column(Float, nullable=False)
    deposit_amount = Column(Float, nullable=False)
    
    # Documents
    rc_number = Column(String, unique=True, index=True)
    insurance_expiry = Column(DateTime(timezone=True))
    fitness_expiry = Column(DateTime(timezone=True))
    
    # Status and Approval
    status = Column(Enum(VehicleStatus), default=VehicleStatus.PENDING_APPROVAL)
    approval_notes = Column(Text)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    
    # Features
    features = Column(Text)  # JSON string of features
    photos = Column(Text)    # JSON array of photo URLs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="vehicles", foreign_keys=[owner_id])
    approver = relationship("User", foreign_keys=[approved_by])
    rentals = relationship("Rental", back_populates="vehicle")
    audit_entries = relationship("AuditEntry", back_populates="vehicle")