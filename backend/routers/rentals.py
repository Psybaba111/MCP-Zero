"""
Rentals API routes
Handles P2P vehicle rentals, booking, and returns
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db, User, Rental, Vehicle, RentalStatus, VehicleStatus
from middleware.auth import get_current_active_user
from services.audit_service import AuditService
from schemas.rentals import RentalCreate, RentalResponse, RentalUpdate, RentalReturnRequest

router = APIRouter()

@router.post("/", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
async def create_rental(
    rental_data: RentalCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Book a vehicle for rental"""
    # Check vehicle exists and is available
    vehicle = db.query(Vehicle).filter(
        and_(
            Vehicle.id == rental_data.vehicle_id,
            Vehicle.status == VehicleStatus.APPROVED
        )
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found or not available"
        )
    
    # Check vehicle is not owned by renter
    if vehicle.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot rent your own vehicle"
        )
    
    # Calculate total amount
    duration_hours = (rental_data.end_time - rental_data.start_time).total_seconds() / 3600
    total_amount = duration_hours * vehicle.hourly_rate
    
    # Create rental
    rental = Rental(
        renter_id=current_user.id,
        vehicle_id=rental_data.vehicle_id,
        start_time=rental_data.start_time,
        end_time=rental_data.end_time,
        hourly_rate=vehicle.hourly_rate,
        total_amount=total_amount,
        deposit_amount=vehicle.deposit_amount
    )
    
    db.add(rental)
    db.commit()
    db.refresh(rental)
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="rental_created",
        user_id=current_user.id,
        entity_type="rental",
        entity_id=rental.id,
        action="created",
        details={
            "vehicle_id": str(rental_data.vehicle_id),
            "duration_hours": duration_hours,
            "total_amount": total_amount,
            "deposit_amount": vehicle.deposit_amount
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return rental

@router.get("/{rental_id}", response_model=RentalResponse)
async def get_rental(
    rental_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get rental details"""
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found"
        )
    
    # Check authorization (renter or vehicle owner)
    vehicle = db.query(Vehicle).filter(Vehicle.id == rental.vehicle_id).first()
    if rental.renter_id != current_user.id and vehicle.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this rental"
        )
    
    return rental

@router.post("/{rental_id}/return", response_model=RentalResponse)
async def return_vehicle(
    rental_id: uuid.UUID,
    return_data: RentalReturnRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Return rented vehicle"""
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found"
        )
    
    # Check authorization (only renter can return)
    if rental.renter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the renter can return the vehicle"
        )
    
    if rental.status != RentalStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rental is not active"
        )
    
    # Update rental with return details
    rental.status = RentalStatus.RETURNED
    rental.return_photos = return_data.return_photos
    rental.return_notes = return_data.return_notes
    rental.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(rental)
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="vehicle_returned",
        user_id=current_user.id,
        entity_type="rental",
        entity_id=rental.id,
        action="returned",
        details={
            "return_photos_count": len(return_data.return_photos) if return_data.return_photos else 0,
            "has_notes": bool(return_data.return_notes)
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    # Emit deposit release event for automation
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="deposit_release",
        user_id=current_user.id,
        entity_type="rental",
        entity_id=rental.id,
        action="deposit_release_requested",
        details={
            "deposit_amount": rental.deposit_amount,
            "rental_total": rental.total_amount
        }
    )
    
    return rental

@router.get("/", response_model=List[RentalResponse])
async def list_rentals(
    status_filter: Optional[RentalStatus] = None,
    vehicle_id: Optional[uuid.UUID] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List user's rentals (as renter or vehicle owner)"""
    # Get rentals where user is either renter or vehicle owner
    query = db.query(Rental).join(Vehicle).filter(
        or_(
            Rental.renter_id == current_user.id,
            Vehicle.owner_id == current_user.id
        )
    )
    
    if status_filter:
        query = query.filter(Rental.status == status_filter)
    
    if vehicle_id:
        query = query.filter(Rental.vehicle_id == vehicle_id)
    
    rentals = query.order_by(Rental.created_at.desc()).offset(offset).limit(limit).all()
    return rentals

@router.put("/{rental_id}", response_model=RentalResponse)
async def update_rental(
    rental_id: uuid.UUID,
    rental_update: RentalUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update rental status"""
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found"
        )
    
    # Check authorization
    vehicle = db.query(Vehicle).filter(Vehicle.id == rental.vehicle_id).first()
    if rental.renter_id != current_user.id and vehicle.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this rental"
        )
    
    # Update rental
    update_data = rental_update.dict(exclude_unset=True)
    old_status = rental.status
    
    for field, value in update_data.items():
        setattr(rental, field, value)
    
    rental.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(rental)
    
    # Log audit event for status changes
    if "status" in update_data and old_status != rental.status:
        await AuditService.log_event(
            correlation_id=getattr(request.state, 'correlation_id', None),
            event_type="rental_status_updated",
            user_id=current_user.id,
            entity_type="rental",
            entity_id=rental.id,
            action="status_updated",
            details={
                "old_status": old_status,
                "new_status": rental.status,
                "updated_by": current_user.role
            },
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
    
    return rental