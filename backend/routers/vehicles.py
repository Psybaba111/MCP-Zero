"""
Vehicles API routes
Handles P2P vehicle listings, search, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db, User, Vehicle, VehicleType, VehicleStatus, UserRole
from middleware.auth import get_current_active_user, require_role
from services.audit_service import AuditService
from schemas.vehicles import VehicleCreate, VehicleResponse, VehicleUpdate, VehicleSearchFilters

router = APIRouter()

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new vehicle listing (pending approval)"""
    # Create vehicle
    vehicle = Vehicle(
        owner_id=current_user.id,
        vehicle_type=vehicle_data.vehicle_type,
        make=vehicle_data.make,
        model=vehicle_data.model,
        year=vehicle_data.year,
        registration_number=vehicle_data.registration_number,
        battery_capacity=vehicle_data.battery_capacity,
        range_km=vehicle_data.range_km,
        hourly_rate=vehicle_data.hourly_rate,
        daily_rate=vehicle_data.daily_rate,
        deposit_amount=vehicle_data.deposit_amount,
        location_lat=vehicle_data.location_lat,
        location_lng=vehicle_data.location_lng,
        photos=vehicle_data.photos,
        features=vehicle_data.features,
        status=VehicleStatus.PENDING  # Requires approval
    )
    
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="vehicle_created",
        user_id=current_user.id,
        entity_type="vehicle",
        entity_id=vehicle.id,
        action="created",
        details={
            "vehicle_type": vehicle_data.vehicle_type,
            "make": vehicle_data.make,
            "model": vehicle_data.model,
            "registration_number": vehicle_data.registration_number,
            "hourly_rate": vehicle_data.hourly_rate,
            "status": "pending"
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return vehicle

@router.get("/", response_model=List[VehicleResponse])
async def search_vehicles(
    vehicle_type: Optional[VehicleType] = Query(None),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(10),
    min_rate: Optional[float] = Query(None),
    max_rate: Optional[float] = Query(None),
    available_only: bool = Query(True),
    limit: int = Query(50),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Search vehicles with filters"""
    query = db.query(Vehicle)
    
    # Only show approved vehicles
    if available_only:
        query = query.filter(Vehicle.status == VehicleStatus.APPROVED)
    
    # Filter by vehicle type
    if vehicle_type:
        query = query.filter(Vehicle.vehicle_type == vehicle_type)
    
    # Filter by rate range
    if min_rate:
        query = query.filter(Vehicle.hourly_rate >= min_rate)
    if max_rate:
        query = query.filter(Vehicle.hourly_rate <= max_rate)
    
    # TODO: Add location-based filtering using lat/lng and radius_km
    # This would require spatial queries or distance calculations
    
    vehicles = query.order_by(Vehicle.created_at.desc()).offset(offset).limit(limit).all()
    return vehicles

@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get vehicle details"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    return vehicle

@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: uuid.UUID,
    vehicle_update: VehicleUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update vehicle details"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Check authorization (owner or admin)
    if vehicle.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this vehicle"
        )
    
    # Update vehicle
    update_data = vehicle_update.dict(exclude_unset=True)
    old_status = vehicle.status
    
    for field, value in update_data.items():
        setattr(vehicle, field, value)
    
    vehicle.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(vehicle)
    
    # Log audit event for status changes
    if "status" in update_data and old_status != vehicle.status:
        await AuditService.log_event(
            correlation_id=getattr(request.state, 'correlation_id', None),
            event_type="vehicle_status_updated",
            user_id=current_user.id,
            entity_type="vehicle",
            entity_id=vehicle.id,
            action="status_updated",
            details={
                "old_status": old_status,
                "new_status": vehicle.status,
                "updated_by": current_user.role
            },
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
    
    return vehicle

@router.get("/my/listings", response_model=List[VehicleResponse])
async def get_my_vehicles(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's vehicle listings"""
    vehicles = db.query(Vehicle).filter(Vehicle.owner_id == current_user.id).all()
    return vehicles

@router.post("/{vehicle_id}/approve", response_model=VehicleResponse)
async def approve_vehicle(
    vehicle_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Approve vehicle listing (admin only)"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    vehicle.status = VehicleStatus.APPROVED
    vehicle.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(vehicle)
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="vehicle_approved",
        user_id=current_user.id,
        entity_type="vehicle",
        entity_id=vehicle.id,
        action="approved",
        details={"approved_by": str(current_user.id)},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return vehicle