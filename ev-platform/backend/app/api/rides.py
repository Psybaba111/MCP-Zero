from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.db.database import get_db
from app.models.ride import Ride, RideType, RideStatus
from app.models.user import User
from app.schemas.ride import (
    RideRequest, RideEstimate, RideCreate, RideResponse, 
    RideStatusUpdate, DriverAssignment, RideTracking, ParcelDetails
)
from app.services.audit_service import audit_service
from app.models.audit import AuditEventType

router = APIRouter()


@router.post("/estimate", response_model=RideEstimate)
async def get_ride_estimate(
    ride_request: RideRequest,
    db: Session = Depends(get_db)
):
    """Get ride fare estimate"""
    try:
        # Calculate distance (in real app, use Google Maps API)
        estimated_distance = 5.2  # km - placeholder
        estimated_duration = 15  # minutes - placeholder
        
        # Calculate fare based on distance and time
        base_fare = 50  # ₹50 base fare
        distance_fare = estimated_distance * 10  # ₹10 per km
        time_fare = estimated_duration * 2  # ₹2 per minute
        
        # Apply surge pricing if needed
        surge_multiplier = 1.0  # In real app, calculate based on demand
        
        total_fare = (base_fare + distance_fare + time_fare) * surge_multiplier
        
        return RideEstimate(
            estimated_distance=estimated_distance,
            estimated_duration=estimated_duration,
            base_fare=base_fare,
            distance_fare=distance_fare,
            time_fare=time_fare,
            surge_multiplier=surge_multiplier,
            total_fare=total_fare
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate estimate: {str(e)}"
        )


@router.post("/", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def create_ride(
    ride_data: RideCreate,
    db: Session = Depends(get_db)
):
    """Create a new ride or parcel delivery request"""
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == ride_data.passenger_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create ride record
        new_ride = Ride(
            ride_type=ride_data.ride_type,
            passenger_id=ride_data.passenger_id,
            pickup_location=ride_data.pickup_location,
            pickup_latitude=ride_data.pickup_latitude,
            pickup_longitude=ride_data.pickup_longitude,
            drop_location=ride_data.drop_location,
            drop_latitude=ride_data.drop_latitude,
            drop_longitude=ride_data.drop_longitude,
            vehicle_type_preference=ride_data.vehicle_type_preference,
            estimated_distance=ride_data.estimated_distance,
            estimated_duration=ride_data.estimated_duration,
            base_fare=ride_data.base_fare,
            distance_fare=ride_data.distance_fare,
            time_fare=ride_data.time_fare,
            surge_multiplier=ride_data.surge_multiplier,
            total_fare=ride_data.total_fare,
            parcel_weight=ride_data.parcel_weight,
            parcel_dimensions=ride_data.parcel_dimensions,
            parcel_description=ride_data.parcel_description,
            parcel_fragile=ride_data.parcel_fragile
        )
        
        db.add(new_ride)
        db.commit()
        db.refresh(new_ride)
        
        # Log ride creation
        await audit_service.log_ride_event(
            ride_id=new_ride.id,
            event_type=AuditEventType.RIDE_CREATED,
            user_id=ride_data.passenger_id,
            status="created"
        )
        
        return new_ride
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ride: {str(e)}"
        )


@router.get("/{ride_id}", response_model=RideResponse)
async def get_ride(
    ride_id: int,
    db: Session = Depends(get_db)
):
    """Get ride details by ID"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    return ride


@router.put("/{ride_id}/status", response_model=RideResponse)
async def update_ride_status(
    ride_id: int,
    status_update: RideStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update ride status"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Update ride status
    ride.status = status_update.status
    
    # Update timestamps based on status
    if status_update.status == RideStatus.ASSIGNED:
        ride.assigned_at = db.query(db.func.now()).scalar()
        ride.driver_id = status_update.driver_id
    elif status_update.status == RideStatus.PICKED_UP:
        ride.picked_up_at = db.query(db.func.now()).scalar()
    elif status_update.status == RideStatus.COMPLETED:
        ride.completed_at = db.query(db.func.now()).scalar()
    
    db.commit()
    db.refresh(ride)
    
    # Log status update
    await audit_service.log_ride_event(
        ride_id=ride_id,
        event_type=AuditEventType.RIDE_COMPLETED if status_update.status == RideStatus.COMPLETED else AuditEventType.RIDE_ASSIGNED,
        user_id=ride.passenger_id,
        status=status_update.status,
        metadata={"driver_id": status_update.driver_id, "notes": status_update.notes}
    )
    
    return ride


@router.post("/{ride_id}/assign-driver", response_model=DriverAssignment)
async def assign_driver(
    ride_id: int,
    driver_assignment: DriverAssignment,
    db: Session = Depends(get_db)
):
    """Assign a driver to a ride"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Validate driver exists
    driver = db.query(User).filter(User.id == driver_assignment.driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Update ride with driver assignment
    ride.driver_id = driver_assignment.driver_id
    ride.status = RideStatus.ASSIGNED
    ride.assigned_at = db.query(db.func.now()).scalar()
    
    db.commit()
    db.refresh(ride)
    
    # Log driver assignment
    await audit_service.log_ride_event(
        ride_id=ride_id,
        event_type=AuditEventType.RIDE_ASSIGNED,
        user_id=ride.passenger_id,
        status="assigned",
        metadata={"driver_id": driver_assignment.driver_id}
    )
    
    return driver_assignment


@router.get("/{ride_id}/tracking", response_model=RideTracking)
async def get_ride_tracking(
    ride_id: int,
    db: Session = Depends(get_db)
):
    """Get real-time ride tracking information"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # In real app, get driver location from GPS service
    driver_location = None
    estimated_arrival = None
    current_location = None
    
    if ride.driver_id:
        # Get driver's current location and ETA
        driver_location = {"lat": 12.9716, "lng": 77.5946}  # Placeholder
        estimated_arrival = 5  # minutes - placeholder
    
    return RideTracking(
        ride_id=ride_id,
        status=ride.status,
        driver_location=driver_location,
        estimated_arrival=estimated_arrival,
        current_location=current_location,
        last_updated=ride.updated_at or ride.created_at
    )


@router.get("/", response_model=List[RideResponse])
async def list_rides(
    user_id: Optional[int] = None,
    status: Optional[RideStatus] = None,
    ride_type: Optional[RideType] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List rides with filters"""
    query = db.query(Ride)
    
    if user_id:
        query = query.filter(Ride.passenger_id == user_id)
    if status:
        query = query.filter(Ride.status == status)
    if ride_type:
        query = query.filter(Ride.ride_type == ride_type)
    
    rides = query.offset(skip).limit(limit).all()
    return rides


@router.post("/{ride_id}/cancel")
async def cancel_ride(
    ride_id: int,
    reason: str,
    db: Session = Depends(get_db)
):
    """Cancel a ride"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if ride.status in [RideStatus.COMPLETED, RideStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or already cancelled ride"
        )
    
    # Update ride status
    ride.status = RideStatus.CANCELLED
    ride.cancelled_at = db.query(db.func.now()).scalar()
    ride.cancellation_reason = reason
    
    db.commit()
    db.refresh(ride)
    
    # Log ride cancellation
    await audit_service.log_ride_event(
        ride_id=ride_id,
        event_type=AuditEventType.RIDE_CANCELLED,
        user_id=ride.passenger_id,
        status="cancelled",
        metadata={"reason": reason}
    )
    
    return {"message": "Ride cancelled successfully", "ride_id": ride_id}


@router.post("/{ride_id}/rate")
async def rate_ride(
    ride_id: int,
    rating: float,
    feedback: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Rate a completed ride"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if ride.status != RideStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only rate completed rides"
        )
    
    if not 1.0 <= rating <= 5.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1.0 and 5.0"
        )
    
    # Update ride rating
    ride.passenger_rating = rating
    
    db.commit()
    db.refresh(ride)
    
    # Log rating
    await audit_service.log_ride_event(
        ride_id=ride_id,
        event_type=AuditEventType.RIDE_COMPLETED,
        user_id=ride.passenger_id,
        status="rated",
        metadata={"rating": rating, "feedback": feedback}
    )
    
    return {"message": "Rating submitted successfully", "ride_id": ride_id, "rating": rating}