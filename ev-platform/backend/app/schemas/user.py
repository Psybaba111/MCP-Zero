from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from ..models.user import UserRole, KYCStatus

# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.PASSENGER

# User Create Schema
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# User Update Schema
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    license_number: Optional[str] = None
    license_expiry: Optional[datetime] = None
    rc_number: Optional[str] = None
    insurance_expiry: Optional[datetime] = None
    fitness_expiry: Optional[datetime] = None

# User Response Schema
class UserResponse(UserBase):
    id: int
    kyc_status: KYCStatus
    kyc_submitted_at: Optional[datetime] = None
    kyc_approved_at: Optional[datetime] = None
    license_verified: bool
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# KYC Request Schema
class KYCRequest(BaseModel):
    license_number: str
    license_expiry: datetime
    rc_number: str
    insurance_expiry: datetime
    fitness_expiry: datetime

# KYC Response Schema
class KYCResponse(BaseModel):
    kyc_status: KYCStatus
    submitted_at: datetime
    approved_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None

# User Login Schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Token Response Schema
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse