from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...models.ride import Ride, RideStatus, RideType
from ...models.user import User
from ...models.audit import Audit, AuditEventType
from ...schemas.ride import (
    RideCreate, RideResponse, RideUpdate, ParcelCreate,
    RideEstimate, RideEstimateResponse
)
from ...core.security import verify_token
from fastapi.security import OAuth2PasswordBearer
import uuid

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# Helper function to get current user from token
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    from jose import JWTError
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

# Helper function to create audit entry
def create_audit_entry(
    db: Session,
    event_type: AuditEventType,
    event_description: str,
    user_id: int = None,
    ride_id: int = None,
    metadata: dict = None,
    request: Request = None
):
    audit_entry = Audit(
        event_type=event_type,
        event_description=event_description,
        user_id=user_id,
        ride_id=ride_id,
        metadata=metadata,
        ip_address=request.client.host if request else None,
        request_id=getattr(request.state, 'request_id', None) if request else None
    )
    db.add(audit_entry)
    db.commit()
    return audit_entry

@router.post("/rides/estimate", response_model=RideEstimateResponse)
async def estimate_ride(
    estimate_data: RideEstimate,
    current_user: User = Depends(get_current_user)
):
    """Get ride fare estimate"""
    # Simple fare calculation logic (can be enhanced with real-time data)
    base_fare = 50.0  # Base fare in INR
    distance_fare = 15.0  # Per km fare
    time_fare = 2.0  # Per minute fare
    
    # Mock distance and time calculation
    estimated_distance = 5.0  # km
    estimated_duration = 20  # minutes
    
    total_fare = base_fare + (distance_fare * estimated_distance) + (time_fare * estimated_duration)
    
    return RideEstimateResponse(
        base_fare=base_fare,
        distance_fare=distance_fare * estimated_distance,
        time_fare=time_fare * estimated_duration,
        total_fare=total_fare,
        estimated_duration=estimated_duration,
        estimated_distance=estimated_distance
    )

@router.post("/rides", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def create_ride(
    ride_data: RideCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Create a new ride booking"""
    # Calculate fare (simplified)
    base_fare = 50.0
    distance_fare = 15.0 * 5.0  # Mock distance
    time_fare = 2.0 * 20  # Mock time
    total_fare = base_fare + distance_fare + time_fare
    
    # Create ride
    db_ride = Ride(
        user_id=current_user.id,
        pickup_address=ride_data.pickup_address,
        pickup_latitude=ride_data.pickup_latitude,
        pickup_longitude=ride_data.pickup_longitude,
        drop_address=ride_data.drop_address,
        drop_latitude=ride_data.drop_latitude,
        drop_longitude=ride_data.drop_longitude,
        type=ride_data.type,
        base_fare=base_fare,
        distance_fare=distance_fare,
        time_fare=time_fare,
        total_fare=total_fare,
        status=RideStatus.CREATED
    )
    
    db.add(db_ride)
    db.commit()
    db.refresh(db_ride)
    
    # Create audit entry
    create_audit_entry(
        db=db,
        event_type=AuditEventType.RIDE_CREATED,
        event_description=f"Ride {db_ride.id} created by user {current_user.email}",
        user_id=current_user.id,
        ride_id=db_ride.id,
        metadata={
            "ride_type": ride_data.type.value,
            "total_fare": total_fare,
            "pickup": ride_data.pickup_address,
            "drop": ride_data.drop_address
        },
        request=request
    )
    
    return db_ride

@router.post("/parcels", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def create_parcel(
    parcel_data: ParcelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Create a new parcel delivery booking"""
    # Calculate fare for parcel (slightly higher base fare)
    base_fare = 75.0
    distance_fare = 15.0 * 5.0  # Mock distance
    time_fare = 2.0 * 20  # Mock time
    weight_fare = parcel_data.parcel_weight * 5.0  # Weight-based fare
    total_fare = base_fare + distance_fare + time_fare + weight_fare
    
    # Create parcel delivery
    db_ride = Ride(
        user_id=current_user.id,
        pickup_address=parcel_data.pickup_address,
        pickup_latitude=parcel_data.pickup_latitude,
        pickup_longitude=parcel_data.pickup_longitude,
        drop_address=parcel_data.drop_address,
        drop_latitude=parcel_data.drop_latitude,
        drop_longitude=parcel_data.drop_longitude,
        type=RideType.PARCEL,
        parcel_description=parcel_data.parcel_description,
        parcel_weight=parcel_data.parcel_weight,
        parcel_dimensions=parcel_data.parcel_dimensions,
        base_fare=base_fare,
        distance_fare=distance_fare,
        time_fare=time_fare,
        total_fare=total_fare,
        status=RideStatus.CREATED
    )
    
    db.add(db_ride)
    db.commit()
    db.refresh(db_ride)
    
    # Create audit entry
    create_audit_entry(
        db=db,
        event_type=AuditEventType.RIDE_CREATED,
        event_description=f"Parcel delivery {db_ride.id} created by user {current_user.email}",
        user_id=current_user.id,
        ride_id=db_ride.id,
        metadata={
            "ride_type": "parcel",
            "total_fare": total_fare,
            "parcel_weight": parcel_data.parcel_weight,
            "pickup": parcel_data.pickup_address,
            "drop": parcel_data.drop_address
        },
        request=request
    )
    
    return db_ride

@router.get("/rides", response_model=List[RideResponse])
async def get_user_rides(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get current user's ride history"""
    rides = db.query(Ride).filter(
        Ride.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return rides

@router.get("/rides/{ride_id}", response_model=RideResponse)
async def get_ride(
    ride_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific ride details"""
    ride = db.query(Ride).filter(
        Ride.id == ride_id,
        Ride.user_id == current_user.id
    ).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    return ride

@router.put("/rides/{ride_id}", response_model=RideResponse)
async def update_ride(
    ride_id: int,
    ride_update: RideUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Update ride status (admin/driver only)"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Update ride fields
    for field, value in ride_update.dict(exclude_unset=True).items():
        setattr(ride, field, value)
    
    db.commit()
    db.refresh(ride)
    
    # Create audit entry for status change
    if ride_update.status:
        create_audit_entry(
            db=db,
            event_type=AuditEventType.RIDE_ASSIGNED if ride_update.status == RideStatus.ASSIGNED else AuditEventType.RIDE_COMPLETED,
            event_description=f"Ride {ride_id} status updated to {ride_update.status}",
            user_id=current_user.id,
            ride_id=ride_id,
            metadata={"new_status": ride_update.status.value},
            request=request
        )
    
    return ride