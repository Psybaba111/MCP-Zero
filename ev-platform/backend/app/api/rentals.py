from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.rental import Rental, RentalStatus
from app.models.vehicle import Vehicle
from app.models.user import User
from app.schemas.rental import (
    RentalRequest, RentalCreate, RentalResponse, RentalStatusUpdate,
    RentalReturn, RentalReturnResponse, RentalCancellation,
    RentalSearch, RentalSummary, RentalOwnerView
)
from app.services.audit_service import audit_service
from app.models.audit import AuditEventType

router = APIRouter()


@router.post("/", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
async def create_rental(
    rental_data: RentalCreate,
    db: Session = Depends(get_db)
):
    """Create a new rental booking"""
    try:
        # Validate renter exists
        renter = db.query(User).filter(User.id == rental_data.renter_id).first()
        if not renter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Renter not found"
            )
        
        # Validate vehicle exists and is available
        vehicle = db.query(Vehicle).filter(Vehicle.id == rental_data.vehicle_id).first()
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        if vehicle.status != "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle is not available for rental"
            )
        
        # Check availability (simplified - in real app, check against existing rentals)
        # For now, assume available
        
        # Create rental record
        new_rental = Rental(
            renter_id=rental_data.renter_id,
            vehicle_id=rental_data.vehicle_id,
            start_time=rental_data.start_time,
            end_time=rental_data.end_time,
            hourly_rate=rental_data.hourly_rate,
            total_hours=rental_data.total_hours,
            total_amount=rental_data.total_amount,
            deposit_amount=rental_data.deposit_amount,
            status=RentalStatus.REQUESTED
        )
        
        db.add(new_rental)
        db.commit()
        db.refresh(new_rental)
        
        # Log rental request
        await audit_service.log_rental_event(
            rental_id=new_rental.id,
            event_type=AuditEventType.RENTAL_REQUESTED,
            user_id=rental_data.renter_id,
            status="requested"
        )
        
        return new_rental
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rental: {str(e)}"
        )


@router.get("/{rental_id}", response_model=RentalResponse)
async def get_rental(
    rental_id: int,
    db: Session = Depends(get_db)
):
    """Get rental details by ID"""
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found"
        )
    return rental


@router.put("/{rental_id}/status", response_model=RentalResponse)
async def update_rental_status(
    rental_id: int,
    status_update: RentalStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update rental status"""
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found"
        )
    
    # Update rental status
    rental.status = status_update.status
    
    # Update timestamps based on status
    if status_update.status == RentalStatus.CONFIRMED:
        rental.confirmed_at = datetime.utcnow()
    elif status_update.status == RentalStatus.ACTIVE:
        rental.started_at = datetime.utcnow()
    elif status_update.status == RentalStatus.COMPLETED:
        rental.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(rental)
    
    # Log status update
    event_type = AuditEventType.RENTAL_CONFIRMED
    if status_update.status == RentalStatus.ACTIVE:
        event_type = AuditEventType.RENTAL_STARTED
    elif status_update.status == RentalStatus.COMPLETED:
        event_type = AuditEventType.RENTAL_COMPLETED
    
    await audit_service.log_rental_event(
        rental_id=rental_id,
        event_type=event_type,
        user_id=rental.renter_id,
        status=status_update.status,
        metadata={"notes": status_update.notes}
    )
    
    return rental


@router.post("/{rental_id}/return", response_model=RentalReturnResponse)
async def return_vehicle(
    rental_id: int,
    return_data: RentalReturn,
    db: Session = Depends(get_db)
):
    """Return a rented vehicle"""
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found"
        )
    
    if rental.status != RentalStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only return active rentals"
        )
    
    # Update rental with return information
    rental.actual_return_time = datetime.utcnow()
    rental.return_photos = return_data.return_photos
    rental.return_odometer = return_data.return_odometer
    rental.return_battery_percentage = return_data.return_battery_percentage
    rental.return_notes = return_data.return_notes
    rental.status = RentalStatus.COMPLETED
    rental.completed_at = datetime.utcnow()
    
    # Release deposit (in real app, this would trigger payment processing)
    rental.deposit_released = True
    rental.deposit_released_at = datetime.utcnow()
    
    db.commit()
    db.refresh(rental)
    
    # Log vehicle return
    await audit_service.log_rental_event(
        rental_id=rental_id,
        event_type=AuditEventType.RENTAL_RETURNED,
        user_id=rental.renter_id,
        status="returned",
        metadata={
            "odometer": return_data.return_odometer,
            "battery": return_data.return_battery_percentage,
            "notes": return_data.return_notes
        }
    )
    
    return RentalReturnResponse(
        rental_id=rental_id,
        status=rental.status,
        deposit_release_status="released",
        deposit_release_time=rental.deposit_released_at,
        return_photos=return_data.return_photos,
        return_odometer=return_data.return_odometer,
        return_battery_percentage=return_data.return_battery_percentage,
        return_notes=return_data.return_notes,
        message="Vehicle returned successfully. Deposit has been released."
    )


@router.post("/{rental_id}/cancel")
async def cancel_rental(
    rental_id: int,
    cancellation_data: RentalCancellation,
    db: Session = Depends(get_db)
):
    """Cancel a rental booking"""
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found"
        )
    
    if rental.status in [RentalStatus.COMPLETED, RentalStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or already cancelled rental"
        )
    
    # Update rental status
    rental.status = RentalStatus.CANCELLED
    rental.cancelled_at = datetime.utcnow()
    rental.cancellation_reason = cancellation_data.cancellation_reason
    rental.refund_amount = cancellation_data.refund_amount
    
    db.commit()
    db.refresh(rental)
    
    # Log rental cancellation
    await audit_service.log_rental_event(
        rental_id=rental_id,
        event_type=AuditEventType.RENTAL_CANCELLED,
        user_id=rental.renter_id,
        status="cancelled",
        metadata={"reason": cancellation_data.cancellation_reason, "refund": cancellation_data.refund_amount}
    )
    
    return {"message": "Rental cancelled successfully", "rental_id": rental_id}


@router.get("/search", response_model=List[RentalResponse])
async def search_rentals(
    vehicle_type: Optional[str] = None,
    location: Optional[str] = None,
    start_time: datetime,
    end_time: datetime,
    max_price_per_hour: Optional[float] = None,
    min_rating: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search for available rental vehicles"""
    # This would typically search through vehicles with availability checking
    # For now, return empty list
    return []


@router.get("/user/{user_id}/summary", response_model=RentalSummary)
async def get_user_rental_summary(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get rental summary for a specific user"""
    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user's rentals (in real app, these would be database queries)
    user_rentals = db.query(Rental).filter(Rental.renter_id == user_id).all()
    
    # Calculate summary statistics
    total_rentals = len(user_rentals)
    active_rentals = len([r for r in user_rentals if r.status == RentalStatus.ACTIVE])
    completed_rentals = len([r for r in user_rentals if r.status == RentalStatus.COMPLETED])
    total_spent = sum([r.total_amount for r in user_rentals if r.status == RentalStatus.COMPLETED])
    
    # Get upcoming and past rentals
    upcoming_rentals = [r for r in user_rentals if r.status in [RentalStatus.CONFIRMED, RentalStatus.ACTIVE]]
    past_rentals = [r for r in user_rentals if r.status in [RentalStatus.COMPLETED, RentalStatus.CANCELLED]]
    
    return RentalSummary(
        total_rentals=total_rentals,
        active_rentals=active_rentals,
        completed_rentals=completed_rentals,
        total_spent=total_spent,
        average_rating=None,  # Would calculate from ratings
        upcoming_rentals=upcoming_rentals,
        past_rentals=past_rentals
    )


@router.get("/{rental_id}/owner-view", response_model=RentalOwnerView)
async def get_rental_owner_view(
    rental_id: int,
    owner_id: int,
    db: Session = Depends(get_db)
):
    """Get rental information for vehicle owner"""
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found"
        )
    
    # Get vehicle and verify ownership
    vehicle = db.query(Vehicle).filter(Vehicle.id == rental.vehicle_id).first()
    if not vehicle or vehicle.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get renter details
    renter = db.query(User).filter(User.id == rental.renter_id).first()
    
    # Calculate earnings
    earnings = rental.total_amount if rental.status == RentalStatus.COMPLETED else 0.0
    
    # Determine deposit status
    deposit_status = "held" if rental.deposit_held and not rental.deposit_released else "released"
    
    return RentalOwnerView(
        rental=rental,
        renter_details={
            "id": renter.id,
            "name": renter.full_name,
            "phone": renter.phone,
            "email": renter.email
        },
        vehicle_details={
            "id": vehicle.id,
            "brand": vehicle.brand,
            "model": vehicle.model,
            "type": vehicle.vehicle_type
        },
        earnings=earnings,
        deposit_status=deposit_status
    )


@router.get("/", response_model=List[RentalResponse])
async def list_rentals(
    user_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    status: Optional[RentalStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List rentals with filters"""
    query = db.query(Rental)
    
    if user_id:
        query = query.filter(Rental.renter_id == user_id)
    if vehicle_id:
        query = query.filter(Rental.vehicle_id == vehicle_id)
    if status:
        query = query.filter(Rental.status == status)
    
    rentals = query.offset(skip).limit(limit).all()
    return rentals