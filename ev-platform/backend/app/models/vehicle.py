from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
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
    MAINTENANCE = "maintenance"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic Info
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    color = Column(String, nullable=False)
    
    # Technical Details
    battery_capacity = Column(Float, nullable=True)  # kWh
    range_km = Column(Float, nullable=True)
    max_speed = Column(Float, nullable=True)  # km/h
    seating_capacity = Column(Integer, nullable=True)
    
    # Rental Details
    hourly_rate = Column(Float, nullable=False)
    daily_rate = Column(Float, nullable=False)
    deposit_amount = Column(Float, nullable=False)
    
    # Location
    pickup_location = Column(Text, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Documents & Compliance
    registration_number = Column(String, nullable=False)
    insurance_number = Column(String, nullable=True)
    fitness_certificate = Column(String, nullable=True)
    puc_certificate = Column(String, nullable=True)
    
    # Status & Approval
    status = Column(Enum(VehicleStatus), default=VehicleStatus.PENDING_APPROVAL)
    approval_notes = Column(Text, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Photos & Media
    photos = Column(Text, nullable=True)  # JSON array of photo URLs
    documents = Column(Text, nullable=True)  # JSON array of document URLs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="vehicles", foreign_keys=[owner_id])
    approver = relationship("User", foreign_keys=[approved_by])
    rentals = relationship("Rental", back_populates="vehicle")
    audit_logs = relationship("AuditLog", back_populates="vehicle")