"""
Pydantic schemas for Users, KYC, and Compliance
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from database import UserRole, KYCStatus

class UserCreate(BaseModel):
    email: EmailStr
    phone: str
    full_name: str
    role: Optional[UserRole] = UserRole.PASSENGER

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    phone: str
    full_name: str
    role: UserRole
    kyc_status: KYCStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class KYCDocumentCreate(BaseModel):
    document_type: str  # "license", "rc", "insurance", "fitness"
    document_url: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    expiry_date: Optional[datetime] = None

class KYCDocumentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    document_type: str
    document_url: Optional[str]
    extracted_data: Optional[Dict[str, Any]]
    status: KYCStatus
    expiry_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class KYCCallbackRequest(BaseModel):
    user_id: uuid.UUID
    document_id: Optional[uuid.UUID] = None
    status: str  # "approved" or "rejected"
    reason: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None