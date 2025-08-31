from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.user import KYCStatus, UserRole


class UserBase(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    full_name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    address: Optional[str] = None
    emergency_contact: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    profile_picture: Optional[str] = None


class UserResponse(UserBase):
    id: int
    kyc_status: KYCStatus
    kyc_requested_at: Optional[datetime]
    kyc_verified_at: Optional[datetime]
    license_number: Optional[str]
    license_expiry: Optional[datetime]
    license_verified: bool
    roles: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class KYCRequest(BaseModel):
    license_number: str
    license_expiry: datetime
    address: str
    emergency_contact: str


class KYCResponse(BaseModel):
    kyc_status: KYCStatus
    police_verification_id: Optional[str]
    message: str


class PoliceKYCCallback(BaseModel):
    verification_id: str
    status: str  # "verified" or "rejected"
    notes: Optional[str] = None
    verified_by: str
    verified_at: datetime


class LicenseUpdate(BaseModel):
    license_number: str
    license_expiry: datetime
    license_verified: bool = False


class UserProfileResponse(BaseModel):
    user: UserResponse
    total_rides: int
    total_rentals: int
    rewards_balance: int
    compliance_score: float