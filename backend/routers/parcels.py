"""
Parcels API routes
Handles parcel delivery booking and tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db, User, Parcel, RideStatus
from middleware.auth import get_current_active_user
from services.audit_service import AuditService
from services.ride_service import ParcelService
from schemas.rides import ParcelCreate, ParcelResponse, ParcelUpdate

router = APIRouter()

@router.post("/", response_model=ParcelResponse, status_code=status.HTTP_201_CREATED)
async def create_parcel(
    parcel_data: ParcelCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new parcel delivery"""
    # Calculate estimated fare
    estimated_fare = await ParcelService.calculate_fare(
        pickup_lat=parcel_data.pickup_lat,
        pickup_lng=parcel_data.pickup_lng,
        drop_lat=parcel_data.drop_lat,
        drop_lng=parcel_data.drop_lng,
        weight_kg=parcel_data.weight_kg
    )
    
    # Create parcel
    parcel = Parcel(
        sender_id=current_user.id,
        pickup_lat=parcel_data.pickup_lat,
        pickup_lng=parcel_data.pickup_lng,
        pickup_address=parcel_data.pickup_address,
        drop_lat=parcel_data.drop_lat,
        drop_lng=parcel_data.drop_lng,
        drop_address=parcel_data.drop_address,
        recipient_name=parcel_data.recipient_name,
        recipient_phone=parcel_data.recipient_phone,
        weight_kg=parcel_data.weight_kg,
        dimensions=parcel_data.dimensions,
        estimated_fare=estimated_fare
    )
    
    db.add(parcel)
    db.commit()
    db.refresh(parcel)
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="parcel_created",
        user_id=current_user.id,
        entity_type="parcel",
        entity_id=parcel.id,
        action="created",
        details={
            "pickup_address": parcel_data.pickup_address,
            "drop_address": parcel_data.drop_address,
            "recipient_name": parcel_data.recipient_name,
            "weight_kg": parcel_data.weight_kg,
            "estimated_fare": estimated_fare
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return parcel

@router.get("/{parcel_id}", response_model=ParcelResponse)
async def get_parcel(
    parcel_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get parcel details"""
    parcel = db.query(Parcel).filter(Parcel.id == parcel_id).first()
    
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel not found"
        )
    
    # Check authorization
    if parcel.sender_id != current_user.id and parcel.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this parcel"
        )
    
    return parcel

@router.put("/{parcel_id}", response_model=ParcelResponse)
async def update_parcel(
    parcel_id: uuid.UUID,
    parcel_update: ParcelUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update parcel status"""
    parcel = db.query(Parcel).filter(Parcel.id == parcel_id).first()
    
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel not found"
        )
    
    # Check authorization
    if parcel.sender_id != current_user.id and parcel.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this parcel"
        )
    
    # Update parcel
    update_data = parcel_update.dict(exclude_unset=True)
    old_status = parcel.status
    
    for field, value in update_data.items():
        setattr(parcel, field, value)
    
    parcel.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(parcel)
    
    # Log audit event for status changes
    if "status" in update_data and old_status != parcel.status:
        await AuditService.log_event(
            correlation_id=getattr(request.state, 'correlation_id', None),
            event_type="parcel_status_updated",
            user_id=current_user.id,
            entity_type="parcel",
            entity_id=parcel.id,
            action="status_updated",
            details={
                "old_status": old_status,
                "new_status": parcel.status,
                "updated_by": current_user.role
            },
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
    
    return parcel

@router.get("/", response_model=List[ParcelResponse])
async def list_parcels(
    status_filter: Optional[RideStatus] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List user's parcels"""
    query = db.query(Parcel).filter(
        (Parcel.sender_id == current_user.id) | (Parcel.driver_id == current_user.id)
    )
    
    if status_filter:
        query = query.filter(Parcel.status == status_filter)
    
    parcels = query.order_by(Parcel.created_at.desc()).offset(offset).limit(limit).all()
    return parcels