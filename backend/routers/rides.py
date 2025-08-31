"""
Rides API routes
Handles ride booking, assignment, and status management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db, User, Ride, RideStatus, VehicleType
from middleware.auth import get_current_active_user
from services.audit_service import AuditService
from services.ride_service import RideService
from schemas.rides import RideCreate, RideResponse, RideUpdate

router = APIRouter()

@router.post("/", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def create_ride(
    ride_data: RideCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new ride booking"""
    # Calculate estimated fare
    estimated_fare = await RideService.calculate_fare(
        pickup_lat=ride_data.pickup_lat,
        pickup_lng=ride_data.pickup_lng,
        drop_lat=ride_data.drop_lat,
        drop_lng=ride_data.drop_lng,
        vehicle_type=ride_data.vehicle_type
    )
    
    # Create ride
    ride = Ride(
        passenger_id=current_user.id,
        pickup_lat=ride_data.pickup_lat,
        pickup_lng=ride_data.pickup_lng,
        pickup_address=ride_data.pickup_address,
        drop_lat=ride_data.drop_lat,
        drop_lng=ride_data.drop_lng,
        drop_address=ride_data.drop_address,
        vehicle_type=ride_data.vehicle_type,
        estimated_fare=estimated_fare
    )
    
    db.add(ride)
    db.commit()
    db.refresh(ride)
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="ride_created",
        user_id=current_user.id,
        entity_type="ride",
        entity_id=ride.id,
        action="created",
        details={
            "pickup_address": ride_data.pickup_address,
            "drop_address": ride_data.drop_address,
            "vehicle_type": ride_data.vehicle_type,
            "estimated_fare": estimated_fare
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return ride

@router.get("/{ride_id}", response_model=RideResponse)
async def get_ride(
    ride_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get ride details"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check authorization
    if ride.passenger_id != current_user.id and ride.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this ride"
        )
    
    return ride

@router.put("/{ride_id}", response_model=RideResponse)
async def update_ride(
    ride_id: uuid.UUID,
    ride_update: RideUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update ride status and details"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check authorization
    if ride.passenger_id != current_user.id and ride.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this ride"
        )
    
    # Update ride
    update_data = ride_update.dict(exclude_unset=True)
    old_status = ride.status
    
    for field, value in update_data.items():
        setattr(ride, field, value)
    
    ride.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ride)
    
    # Log audit event for status changes
    if "status" in update_data and old_status != ride.status:
        await AuditService.log_event(
            correlation_id=getattr(request.state, 'correlation_id', None),
            event_type="ride_status_updated",
            user_id=current_user.id,
            entity_type="ride",
            entity_id=ride.id,
            action="status_updated",
            details={
                "old_status": old_status,
                "new_status": ride.status,
                "updated_by": current_user.role
            },
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
    
    return ride

@router.get("/", response_model=List[RideResponse])
async def list_rides(
    status_filter: Optional[RideStatus] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List user's rides"""
    query = db.query(Ride).filter(
        (Ride.passenger_id == current_user.id) | (Ride.driver_id == current_user.id)
    )
    
    if status_filter:
        query = query.filter(Ride.status == status_filter)
    
    rides = query.order_by(Ride.created_at.desc()).offset(offset).limit(limit).all()
    return rides

@router.post("/{ride_id}/assign", response_model=RideResponse)
async def assign_driver(
    ride_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Assign driver to ride (placeholder implementation)"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if ride.status != RideStatus.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ride must be paid before assignment"
        )
    
    # Placeholder driver assignment logic
    ride.driver_id = current_user.id  # In real implementation, use driver matching algorithm
    ride.status = RideStatus.ASSIGNED
    ride.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ride)
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="ride_assigned",
        user_id=current_user.id,
        entity_type="ride",
        entity_id=ride.id,
        action="assigned",
        details={"driver_id": str(current_user.id)},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return ride