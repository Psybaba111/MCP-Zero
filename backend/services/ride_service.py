"""
Ride Service for EV Platform
Business logic for ride booking, fare calculation, and driver assignment
"""

from typing import Optional
import math
from database import VehicleType

class RideService:
    """Service for ride-related operations"""
    
    # Base fare configuration (in INR)
    BASE_FARE = {
        VehicleType.CYCLE: 10,
        VehicleType.SCOOTER: 20,
        VehicleType.BIKE: 30,
        VehicleType.CAR: 50
    }
    
    RATE_PER_KM = {
        VehicleType.CYCLE: 5,
        VehicleType.SCOOTER: 8,
        VehicleType.BIKE: 12,
        VehicleType.CAR: 15
    }
    
    @staticmethod
    def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    async def calculate_fare(
        pickup_lat: float,
        pickup_lng: float,
        drop_lat: float,
        drop_lng: float,
        vehicle_type: VehicleType
    ) -> float:
        """Calculate estimated fare for a ride"""
        distance = RideService.calculate_distance(pickup_lat, pickup_lng, drop_lat, drop_lng)
        
        base_fare = RideService.BASE_FARE.get(vehicle_type, 50)
        rate_per_km = RideService.RATE_PER_KM.get(vehicle_type, 15)
        
        total_fare = base_fare + (distance * rate_per_km)
        
        # Minimum fare
        minimum_fare = base_fare * 2
        return max(total_fare, minimum_fare)
    
    @staticmethod
    async def assign_placeholder_driver(ride_id: uuid.UUID, db: Session) -> Optional[uuid.UUID]:
        """Placeholder driver assignment logic"""
        # In a real implementation, this would:
        # 1. Find nearby available drivers
        # 2. Check driver ratings and preferences
        # 3. Use matching algorithm
        # For now, we'll just return None to indicate no driver assigned yet
        return None

class ParcelService:
    """Service for parcel delivery operations"""
    
    # Parcel fare configuration
    BASE_FARE = 25  # Base fare for parcels
    RATE_PER_KM = 10
    WEIGHT_MULTIPLIER = 2  # Additional charge per kg
    
    @staticmethod
    async def calculate_fare(
        pickup_lat: float,
        pickup_lng: float,
        drop_lat: float,
        drop_lng: float,
        weight_kg: Optional[float] = None
    ) -> float:
        """Calculate estimated fare for parcel delivery"""
        distance = RideService.calculate_distance(pickup_lat, pickup_lng, drop_lat, drop_lng)
        
        base_fare = ParcelService.BASE_FARE
        distance_fare = distance * ParcelService.RATE_PER_KM
        weight_fare = (weight_kg or 1) * ParcelService.WEIGHT_MULTIPLIER
        
        total_fare = base_fare + distance_fare + weight_fare
        
        # Minimum fare
        minimum_fare = 50
        return max(total_fare, minimum_fare)