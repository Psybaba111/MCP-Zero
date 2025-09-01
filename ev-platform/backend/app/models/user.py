from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class UserRole(str, enum.Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"
    OWNER = "owner"
    ADMIN = "admin"

class KYCStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PASSENGER)
    
    # KYC and Compliance
    kyc_status = Column(Enum(KYCStatus), default=KYCStatus.PENDING)
    kyc_submitted_at = Column(DateTime(timezone=True))
    kyc_approved_at = Column(DateTime(timezone=True))
    kyc_rejected_reason = Column(Text)
    
    # License Information
    license_number = Column(String, unique=True, index=True)
    license_expiry = Column(DateTime(timezone=True))
    license_verified = Column(Boolean, default=False)
    
    # Vehicle Documents
    rc_number = Column(String, unique=True, index=True)
    insurance_expiry = Column(DateTime(timezone=True))
    fitness_expiry = Column(DateTime(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    rides = relationship("Ride", back_populates="user")
    parcels = relationship("Parcel", back_populates="user")
    rentals = relationship("Rental", back_populates="user")
    vehicles = relationship("Vehicle", back_populates="owner")
    rewards = relationship("Reward", back_populates="user")
    audit_entries = relationship("AuditEntry", back_populates="user")