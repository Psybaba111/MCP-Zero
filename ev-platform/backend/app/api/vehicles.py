from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.vehicle import Vehicle, VehicleType, VehicleStatus
from app.models.user import User
from app.schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleResponse, VehicleApproval,
    VehicleSearch, VehicleAvailability, VehicleOwnerResponse
)
from app.services.audit_service import audit_service
from app.models.audit import AuditEventType

router = APIRouter()


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    owner_id: int,
    db: Session = Depends(get_db)
):
    """Create a new vehicle listing"""
    try:
        # Validate owner exists
        owner = db.query(User).filter(User.id == owner_id).first()
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Owner not found"
            )
        
        # Create vehicle listing
        new_vehicle = Vehicle(
            owner_id=owner_id,
            vehicle_type=vehicle_data.vehicle_type,
            brand=vehicle_data.brand,
            model=vehicle_data.model,
            year=vehicle_data.year,
            color=vehicle_data.color,
            battery_capacity=vehicle_data.battery_capacity,
            range_km=vehicle_data.range_km,
            max_speed=vehicle_data.max_speed,
            seating_capacity=vehicle_data.seating_capacity,
            hourly_rate=vehicle_data.hourly_rate,
            daily_rate=vehicle_data.daily_rate,
            deposit_amount=vehicle_data.deposit_amount,
            pickup_location=vehicle_data.pickup_location,
            latitude=vehicle_data.latitude,
            longitude=vehicle_data.longitude,
            registration_number=vehicle_data.registration_number,
            insurance_number=vehicle_data.insurance_number,
            fitness_certificate=vehicle_data.fitness_certificate,
            puc_certificate=vehicle_data.puc_certificate,
            photos=vehicle_data.photos,
            documents=vehicle_data.documents,
            status=VehicleStatus.PENDING_APPROVAL
        )
        
        db.add(new_vehicle)
        db.commit()
        db.refresh(new_vehicle)
        
        # Log vehicle listing
        await audit_service.log_event(
            event_type=AuditEventType.VEHICLE_LISTED,
            user_id=owner_id,
            vehicle_id=new_vehicle.id,
            event_data={"vehicle_type": vehicle_data.vehicle_type, "brand": vehicle_data.brand}
        )
        
        return new_vehicle
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create vehicle listing: {str(e)}"
        )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """Get vehicle details by ID"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    owner_id: int,
    db: Session = Depends(get_db)
):
    """Update vehicle listing"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Verify ownership
    if vehicle.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can update this vehicle"
        )
    
    # Update vehicle fields
    for field, value in vehicle_data.dict(exclude_unset=True).items():
        setattr(vehicle, field, value)
    
    # Reset approval status if significant changes made
    if any(field in vehicle_data.dict(exclude_unset=True) for field in ['registration_number', 'insurance_number', 'fitness_certificate']):
        vehicle.status = VehicleStatus.PENDING_APPROVAL
        vehicle.approved_by = None
        vehicle.approved_at = None
    
    db.commit()
    db.refresh(vehicle)
    
        # Log vehicle update
        await audit_service.log_event(
            event_type=AuditEventType.VEHICLE_LISTED,
            user_id=owner_id,
            vehicle_id=vehicle_id,
            event_data={"updated_fields": list(vehicle_data.dict(exclude_unset=True).keys())}
        )
    
    return vehicle


@router.post("/{vehicle_id}/approve", response_model=VehicleResponse)
async def approve_vehicle(
    vehicle_id: int,
    approval_data: VehicleApproval,
    db: Session = Depends(get_db)
):
    """Approve or reject a vehicle listing (admin/ops only)"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Update approval status
    vehicle.status = approval_data.status
    vehicle.approval_notes = approval_data.approval_notes
    vehicle.approved_by = approval_data.approved_by
    vehicle.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(vehicle)
    
    # Log approval decision
    await audit_service.log_event(
        event_type=AuditEventType.VEHICLE_APPROVED if approval_data.status == VehicleStatus.APPROVED else AuditEventType.VEHICLE_REJECTED,
        user_id=vehicle.owner_id,
        vehicle_id=vehicle_id,
        event_data={"status": approval_data.status, "notes": approval_data.approval_notes}
    )
    
    return vehicle


@router.get("/search", response_model=List[VehicleResponse])
async def search_vehicles(
    vehicle_type: Optional[VehicleType] = None,
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: float = 10.0,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    available_from: Optional[datetime] = None,
    available_until: Optional[datetime] = None,
    max_distance: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search for available vehicles with filters"""
    query = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.APPROVED)
    
    # Apply filters
    if vehicle_type:
        query = query.filter(Vehicle.vehicle_type == vehicle_type)
    
    if min_price is not None:
        query = query.filter(Vehicle.hourly_rate >= min_price)
    
    if max_price is not None:
        query = query.filter(Vehicle.hourly_rate <= max_price)
    
    if max_distance is not None:
        query = query.filter(Vehicle.range_km >= max_distance)
    
    # Location-based filtering (simplified - in real app, use geospatial queries)
    if location:
        query = query.filter(Vehicle.pickup_location.ilike(f"%{location}%"))
    
    # Availability filtering (simplified - in real app, check against existing rentals)
    if available_from and available_until:
        # This would require complex availability checking logic
        pass
    
    vehicles = query.offset(skip).limit(limit).all()
    return vehicles


@router.get("/{vehicle_id}/availability", response_model=VehicleAvailability)
async def get_vehicle_availability(
    vehicle_id: int,
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db)
):
    """Check vehicle availability for a specific time slot"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # In real app, check against existing rentals
    # For now, return placeholder data
    available_slots = [
        {
            "start_time": start_time,
            "end_time": end_time,
            "is_available": True
        }
    ]
    
    return VehicleAvailability(
        vehicle_id=vehicle_id,
        available_slots=available_slots,
        next_available=start_time,
        is_available_now=True
    )


@router.get("/owner/{owner_id}", response_model=List[VehicleResponse])
async def get_owner_vehicles(
    owner_id: int,
    status: Optional[VehicleStatus] = None,
    db: Session = Depends(get_db)
):
    """Get all vehicles owned by a specific user"""
    query = db.query(Vehicle).filter(Vehicle.owner_id == owner_id)
    
    if status:
        query = query.filter(Vehicle.status == status)
    
    vehicles = query.all()
    return vehicles


@router.get("/{vehicle_id}/owner-view", response_model=VehicleOwnerResponse)
async def get_vehicle_owner_view(
    vehicle_id: int,
    owner_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive vehicle information for owner dashboard"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    if vehicle.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can view this information"
        )
    
    # Calculate statistics (in real app, these would be database queries)
    total_earnings = 0.0  # Sum of all rental payments
    total_rentals = 0  # Count of completed rentals
    average_rating = None  # Average rating from renters
    upcoming_bookings = []  # List of upcoming rental bookings
    
    return VehicleOwnerResponse(
        vehicle=vehicle,
        total_earnings=total_earnings,
        total_rentals=total_rentals,
        average_rating=average_rating,
        upcoming_bookings=upcoming_bookings
    )


@router.delete("/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: int,
    owner_id: int,
    db: Session = Depends(get_db)
):
    """Delete a vehicle listing"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Verify ownership
    if vehicle.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete this vehicle"
        )
    
    # Check if vehicle has active rentals
    # In real app, check for active rentals before deletion
    
    # Soft delete by setting status to inactive
    vehicle.status = VehicleStatus.INACTIVE
    
    db.commit()
    
    # Log vehicle deletion
    await audit_service.log_event(
        event_type=AuditEventType.VEHICLE_LISTED,
        user_id=owner_id,
        vehicle_id=vehicle_id,
        event_data={"action": "deleted", "status": "inactive"}
    )
    
    return {"message": "Vehicle listing deleted successfully", "vehicle_id": vehicle_id}