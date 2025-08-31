"""
Users, KYC, and Compliance API routes
Handles user management, KYC status, and compliance callbacks
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db, User, KYCDocument, UserRole, KYCStatus
from middleware.auth import get_current_active_user, create_access_token
from services.audit_service import AuditService
from schemas.users import (
    UserCreate, UserResponse, UserUpdate,
    KYCDocumentCreate, KYCDocumentResponse,
    KYCCallbackRequest, LoginRequest, TokenResponse
)

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user"""
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
    user = User(
        email=user_data.email,
        phone=user_data.phone,
        full_name=user_data.full_name,
        role=user_data.role or UserRole.PASSENGER
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="user_registered",
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        action="created",
        details={
            "email": user.email,
            "role": user.role,
            "ip_address": request.client.host
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return user

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login user and return JWT token"""
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="user_login",
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        action="login",
        details={"ip_address": request.client.host},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="user_updated",
        user_id=current_user.id,
        entity_type="user",
        entity_id=current_user.id,
        action="updated",
        details=update_data,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return current_user

@router.post("/kyc/documents", response_model=KYCDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_kyc_document(
    doc_data: KYCDocumentCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload KYC document"""
    kyc_doc = KYCDocument(
        user_id=current_user.id,
        document_type=doc_data.document_type,
        document_url=doc_data.document_url,
        extracted_data=doc_data.extracted_data,
        expiry_date=doc_data.expiry_date
    )
    
    db.add(kyc_doc)
    db.commit()
    db.refresh(kyc_doc)
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="kyc_document_uploaded",
        user_id=current_user.id,
        entity_type="kyc_document",
        entity_id=kyc_doc.id,
        action="created",
        details={
            "document_type": doc_data.document_type,
            "has_extracted_data": bool(doc_data.extracted_data)
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return kyc_doc

@router.get("/kyc/documents", response_model=List[KYCDocumentResponse])
async def get_kyc_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's KYC documents"""
    documents = db.query(KYCDocument).filter(KYCDocument.user_id == current_user.id).all()
    return documents

@router.post("/events/kyc.requested", status_code=status.HTTP_200_OK)
async def kyc_requested_event(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Handle KYC requested event"""
    # Update user KYC status to in_progress
    current_user.kyc_status = KYCStatus.IN_PROGRESS
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="kyc_requested",
        user_id=current_user.id,
        entity_type="user",
        entity_id=current_user.id,
        action="kyc_status_updated",
        details={"new_status": "in_progress"},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "KYC request processed", "status": "success"}

@router.post("/callbacks/kyc", status_code=status.HTTP_200_OK)
async def kyc_callback(
    callback_data: KYCCallbackRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle KYC callback from compliance service"""
    # Find user and document
    user = db.query(User).filter(User.id == callback_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update KYC status
    if callback_data.status == "approved":
        user.kyc_status = KYCStatus.APPROVED
        # If driver, set them as active
        if user.role == UserRole.DRIVER:
            user.is_active = True
    else:
        user.kyc_status = KYCStatus.REJECTED
    
    user.updated_at = datetime.utcnow()
    
    # Update document if provided
    if callback_data.document_id:
        document = db.query(KYCDocument).filter(
            KYCDocument.id == callback_data.document_id
        ).first()
        if document:
            document.status = KYCStatus.APPROVED if callback_data.status == "approved" else KYCStatus.REJECTED
            document.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="kyc_callback_received",
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        action="kyc_status_updated",
        details={
            "new_status": callback_data.status,
            "document_id": str(callback_data.document_id) if callback_data.document_id else None,
            "callback_source": "compliance_service"
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "KYC callback processed", "status": "success"}

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only or self)"""
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    kyc_status: Optional[KYCStatus] = None,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List users (admin only)"""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if kyc_status:
        query = query.filter(User.kyc_status == kyc_status)
    
    users = query.offset(skip).limit(limit).all()
    return users