from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...core.security import get_password_hash, verify_password, create_access_token, verify_token
from ...models.user import User, KYCStatus
from ...schemas.user import (
    UserCreate, UserResponse, UserUpdate, UserLogin, 
    TokenResponse, KYCRequest, KYCResponse
)
from ...models.audit import Audit, AuditEventType
from ...core.config import settings
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.sql import func
from jose import JWTError
import json

router = APIRouter()

# Helper function to create audit entry
def create_audit_entry(
    db: Session,
    event_type: AuditEventType,
    event_description: str,
    user_id: int = None,
    admin_id: int = None,
    metadata: dict = None,
    request: Request = None
):
    audit_entry = Audit(
        event_type=event_type,
        event_description=event_description,
        user_id=user_id,
        admin_id=admin_id,
        metadata=metadata,
        ip_address=request.client.host if request else None,
        request_id=getattr(request.state, 'request_id', None) if request else None
    )
    db.add(audit_entry)
    db.commit()
    return audit_entry

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Create a new user account"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.phone == user_data.phone)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or phone already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        phone=user_data.phone,
        full_name=user_data.full_name,
        password_hash=hashed_password,
        role=user_data.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create audit entry
    create_audit_entry(
        db=db,
        event_type=AuditEventType.USER_CREATED,
        event_description=f"User {db_user.email} created",
        user_id=db_user.id,
        metadata={"email": db_user.email, "role": db_user.role.value},
        request=request
    )
    
    return db_user

@router.post("/users/login", response_model=TokenResponse)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Authenticate user and return access token"""
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )

@router.get("/users/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    return current_user

@router.put("/users/me", response_model=UserResponse)
async def update_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Update current user profile"""
    # Update user fields
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    # Create audit entry
    create_audit_entry(
        db=db,
        event_type=AuditEventType.USER_UPDATED,
        event_description=f"User {current_user.email} profile updated",
        user_id=current_user.id,
        metadata={"updated_fields": list(user_data.dict(exclude_unset=True).keys())},
        request=request
    )
    
    return current_user

@router.post("/users/kyc", response_model=KYCResponse)
async def submit_kyc(
    kyc_data: KYCRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Submit KYC documents for verification"""
    if current_user.kyc_status == KYCStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="KYC already approved"
        )
    
    # Update user with KYC information
    current_user.license_number = kyc_data.license_number
    current_user.license_expiry = kyc_data.license_expiry
    current_user.rc_number = kyc_data.rc_number
    current_user.insurance_expiry = kyc_data.insurance_expiry
    current_user.fitness_expiry = kyc_data.fitness_expiry
    current_user.kyc_status = KYCStatus.PENDING
    current_user.kyc_submitted_at = func.now()
    
    db.commit()
    db.refresh(current_user)
    
    # Create audit entry
    create_audit_entry(
        db=db,
        event_type=AuditEventType.KYC_REQUESTED,
        event_description=f"KYC submitted for user {current_user.email}",
        user_id=current_user.id,
        metadata={"kyc_type": "driver_verification"},
        request=request
    )
    
    return KYCResponse(
        kyc_status=current_user.kyc_status,
        submitted_at=current_user.kyc_submitted_at
    )

@router.get("/users/kyc/status", response_model=KYCResponse)
async def get_kyc_status(
    current_user: User = Depends(get_current_user)
):
    """Get current user's KYC status"""
    return KYCResponse(
        kyc_status=current_user.kyc_status,
        submitted_at=current_user.kyc_submitted_at,
        approved_at=current_user.kyc_approved_at,
        rejected_reason=current_user.kyc_rejected_reason
    )

# Helper function to get current user from token
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")