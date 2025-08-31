from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class KYCStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class UserRole(str, enum.Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"
    OWNER = "owner"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # KYC & Compliance
    kyc_status = Column(Enum(KYCStatus), default=KYCStatus.PENDING)
    kyc_requested_at = Column(DateTime(timezone=True), server_default=func.now())
    kyc_verified_at = Column(DateTime(timezone=True), nullable=True)
    police_verification_id = Column(String, nullable=True)
    
    # License & Documents
    license_number = Column(String, nullable=True)
    license_expiry = Column(DateTime(timezone=True), nullable=True)
    license_verified = Column(Boolean, default=False)
    
    # Profile
    profile_picture = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact = Column(String, nullable=True)
    
    # Roles & Status
    roles = Column(String, default=UserRole.PASSENGER)  # Comma-separated roles
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    rides = relationship("Ride", back_populates="passenger")
    vehicles = relationship("Vehicle", back_populates="owner")
    rentals = relationship("Rental", back_populates="renter")
    audit_logs = relationship("AuditLog", back_populates="user")
    rewards = relationship("Reward", back_populates="user")