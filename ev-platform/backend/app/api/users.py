from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.database import get_db
from app.models.user import User, KYCStatus
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, KYCRequest, 
    KYCResponse, PoliceKYCCallback, LicenseUpdate, UserProfileResponse
)
from app.services.audit_service import audit_service
from app.models.audit import AuditEventType

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user account"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.phone == user_data.phone)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or phone already exists"
            )
        
        # Create new user (in real app, hash password)
        new_user = User(
            email=user_data.email,
            phone=user_data.phone,
            full_name=user_data.full_name,
            hashed_password=user_data.password,  # Should be hashed
            address=user_data.address,
            emergency_contact=user_data.emergency_contact
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log user creation
        await audit_service.log_event(
            event_type=AuditEventType.USER_CREATED,
            user_id=new_user.id,
            event_data={"email": user_data.email, "phone": user_data.phone}
        )
        
        return new_user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user profile"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Log user update
    await audit_service.log_event(
        event_type=AuditEventType.USER_UPDATED,
        user_id=user_id,
        event_data={"updated_fields": list(user_data.dict(exclude_unset=True).keys())}
    )
    
    return user


@router.post("/{user_id}/kyc", response_model=KYCResponse)
async def request_kyc(
    user_id: int,
    kyc_data: KYCRequest,
    db: Session = Depends(get_db)
):
    """Request KYC verification for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user with KYC information
    user.license_number = kyc_data.license_number
    user.license_expiry = kyc_data.license_expiry
    user.address = kyc_data.address
    user.emergency_contact = kyc_data.emergency_contact
    user.kyc_status = KYCStatus.PENDING
    user.kyc_requested_at = db.query(db.func.now()).scalar()
    
    # Generate police verification ID
    police_verification_id = f"KYC_{uuid.uuid4().hex[:8].upper()}"
    user.police_verification_id = police_verification_id
    
    db.commit()
    db.refresh(user)
    
    # Log KYC request
    await audit_service.log_kyc_event(
        user_id=user_id,
        event_type=AuditEventType.KYC_REQUESTED,
        police_verification_id=police_verification_id
    )
    
    return KYCResponse(
        kyc_status=user.kyc_status,
        police_verification_id=police_verification_id,
        message="KYC request submitted successfully. Police verification in progress."
    )


@router.post("/kyc/police-callback", response_model=dict)
async def police_kyc_callback(
    callback_data: PoliceKYCCallback,
    db: Session = Depends(get_db)
):
    """Police KYC verification callback"""
    # Find user by verification ID
    user = db.query(User).filter(
        User.police_verification_id == callback_data.verification_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC verification ID not found"
        )
    
    # Update KYC status based on police response
    if callback_data.status == "verified":
        user.kyc_status = KYCStatus.VERIFIED
        user.kyc_verified_at = callback_data.verified_at
        user.is_verified = True
        message = "KYC verification completed successfully"
        event_type = AuditEventType.KYC_VERIFIED
    else:
        user.kyc_status = KYCStatus.REJECTED
        message = f"KYC verification rejected: {callback_data.notes}"
        event_type = AuditEventType.KYC_REJECTED
    
    db.commit()
    db.refresh(user)
    
    # Log KYC callback
    await audit_service.log_kyc_event(
        user_id=user.id,
        event_type=event_type,
        notes=callback_data.notes
    )
    
    return {
        "message": message,
        "user_id": user.id,
        "kyc_status": user.kyc_status,
        "verified_at": user.kyc_verified_at if user.kyc_verified_at else None
    }


@router.put("/{user_id}/license", response_model=UserResponse)
async def update_license(
    user_id: int,
    license_data: LicenseUpdate,
    db: Session = Depends(get_db)
):
    """Update user's license information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update license information
    user.license_number = license_data.license_number
    user.license_expiry = license_data.license_expiry
    user.license_verified = license_data.license_verified
    
    db.commit()
    db.refresh(user)
    
    # Log license update
    await audit_service.log_event(
        event_type=AuditEventType.USER_UPDATED,
        user_id=user_id,
        event_data={"license_updated": True, "expiry": str(license_data.license_expiry)}
    )
    
    return user


@router.get("/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive user profile with statistics"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Calculate profile statistics (in real app, these would be database queries)
    total_rides = 0  # db.query(Ride).filter(Ride.passenger_id == user_id).count()
    total_rentals = 0  # db.query(Rental).filter(Rental.renter_id == user_id).count()
    rewards_balance = 0  # db.query(Reward).filter(Reward.user_id == user_id, Reward.status == "accrued").sum(Reward.points_earned)
    
    # Calculate compliance score
    compliance_score = 0.0
    if user.kyc_status == KYCStatus.VERIFIED:
        compliance_score += 40.0
    if user.license_verified:
        compliance_score += 30.0
    if user.is_active:
        compliance_score += 20.0
    if user.address and user.emergency_contact:
        compliance_score += 10.0
    
    return UserProfileResponse(
        user=user,
        total_rides=total_rides,
        total_rentals=total_rentals,
        rewards_balance=rewards_balance,
        compliance_score=compliance_score
    )


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List users with pagination"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users