"""
Database configuration and models for EV Platform
Uses PostgreSQL with SQLAlchemy ORM
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import os
import enum

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/ev_platform")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class UserRole(str, enum.Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"
    OWNER = "owner"
    ADMIN = "admin"

class KYCStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"

class RideStatus(str, enum.Enum):
    CREATED = "created"
    PAID = "paid"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class VehicleType(str, enum.Enum):
    CAR = "car"
    BIKE = "bike"
    SCOOTER = "scooter"
    CYCLE = "cycle"

class VehicleStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    INACTIVE = "inactive"

class RentalStatus(str, enum.Enum):
    CREATED = "created"
    PAID = "paid"
    ACTIVE = "active"
    RETURNED = "returned"
    CANCELLED = "cancelled"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PASSENGER)
    kyc_status = Column(Enum(KYCStatus), default=KYCStatus.PENDING)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rides_as_passenger = relationship("Ride", foreign_keys="Ride.passenger_id", back_populates="passenger")
    rides_as_driver = relationship("Ride", foreign_keys="Ride.driver_id", back_populates="driver")
    vehicles = relationship("Vehicle", back_populates="owner")
    rentals_as_renter = relationship("Rental", foreign_keys="Rental.renter_id", back_populates="renter")

class KYCDocument(Base):
    __tablename__ = "kyc_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    document_type = Column(String, nullable=False)  # "license", "rc", "insurance", "fitness"
    document_url = Column(String)
    extracted_data = Column(JSONB)
    status = Column(Enum(KYCStatus), default=KYCStatus.PENDING)
    expiry_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer)
    registration_number = Column(String, unique=True, nullable=False)
    battery_capacity = Column(Float)  # kWh
    range_km = Column(Float)
    hourly_rate = Column(Float, nullable=False)
    daily_rate = Column(Float, nullable=False)
    deposit_amount = Column(Float, nullable=False)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.PENDING)
    location_lat = Column(Float)
    location_lng = Column(Float)
    photos = Column(JSONB)  # Array of photo URLs
    features = Column(JSONB)  # Array of features
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="vehicles")
    rentals = relationship("Rental", back_populates="vehicle")

class Ride(Base):
    __tablename__ = "rides"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    passenger_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    pickup_lat = Column(Float, nullable=False)
    pickup_lng = Column(Float, nullable=False)
    pickup_address = Column(String, nullable=False)
    drop_lat = Column(Float, nullable=False)
    drop_lng = Column(Float, nullable=False)
    drop_address = Column(String, nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    estimated_fare = Column(Float)
    final_fare = Column(Float)
    status = Column(Enum(RideStatus), default=RideStatus.CREATED)
    payment_intent_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    passenger = relationship("User", foreign_keys=[passenger_id], back_populates="rides_as_passenger")
    driver = relationship("User", foreign_keys=[driver_id], back_populates="rides_as_driver")

class Parcel(Base):
    __tablename__ = "parcels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    pickup_lat = Column(Float, nullable=False)
    pickup_lng = Column(Float, nullable=False)
    pickup_address = Column(String, nullable=False)
    drop_lat = Column(Float, nullable=False)
    drop_lng = Column(Float, nullable=False)
    drop_address = Column(String, nullable=False)
    recipient_name = Column(String, nullable=False)
    recipient_phone = Column(String, nullable=False)
    weight_kg = Column(Float)
    dimensions = Column(JSONB)  # {length, width, height}
    estimated_fare = Column(Float)
    final_fare = Column(Float)
    status = Column(Enum(RideStatus), default=RideStatus.CREATED)
    payment_intent_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Rental(Base):
    __tablename__ = "rentals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    renter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    hourly_rate = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    deposit_amount = Column(Float, nullable=False)
    status = Column(Enum(RentalStatus), default=RentalStatus.CREATED)
    payment_intent_id = Column(String)
    deposit_payment_intent_id = Column(String)
    return_photos = Column(JSONB)  # Photos at return
    return_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    renter = relationship("User", foreign_keys=[renter_id], back_populates="rentals_as_renter")
    vehicle = relationship("Vehicle", back_populates="rentals")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_intent_id = Column(String, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    entity_type = Column(String, nullable=False)  # "ride", "parcel", "rental", "deposit"
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    hyperswitch_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RewardAccount(Base):
    __tablename__ = "reward_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    points_balance = Column(Integer, default=0)
    tier = Column(String, default="bronze")  # bronze, silver, gold, platinum
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RewardEvent(Base):
    __tablename__ = "reward_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False)  # "ride_completed", "kyc_completed", "rental_on_time"
    points_earned = Column(Integer, nullable=False)
    entity_type = Column(String)  # "ride", "rental", "kyc"
    entity_id = Column(UUID(as_uuid=True))
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    correlation_id = Column(String, index=True)
    event_type = Column(String, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    entity_type = Column(String)  # "user", "ride", "vehicle", "payment", etc.
    entity_id = Column(UUID(as_uuid=True))
    action = Column(String, nullable=False)  # "created", "updated", "deleted", "payment_completed"
    details = Column(JSONB)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# Database dependency
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)