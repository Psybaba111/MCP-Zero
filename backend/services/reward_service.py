"""
Reward Service for EV Platform
Handles points calculation, tier management, and fraud detection
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from database import RewardEvent, User

class RewardService:
    """Service for reward points and tier management"""
    
    # Points rules configuration
    POINTS_RULES = {
        "ride_completed": 10,
        "parcel_delivered": 15,
        "rental_completed": 25,
        "rental_on_time": 10,  # Bonus for returning on time
        "kyc_completed": 100,
        "first_ride": 50,
        "referral": 200,
        "review_submitted": 5
    }
    
    # Daily caps to prevent abuse
    DAILY_CAPS = {
        "ride_completed": 500,  # Max 50 rides worth of points per day
        "parcel_delivered": 300,
        "rental_completed": 200,
        "review_submitted": 25
    }
    
    # Tier thresholds
    TIER_THRESHOLDS = {
        "bronze": 0,
        "silver": 1000,
        "gold": 5000,
        "platinum": 15000
    }
    
    @staticmethod
    async def calculate_points(
        event_type: str,
        metadata: Optional[Dict[str, Any]],
        user_id: uuid.UUID,
        db: Session
    ) -> int:
        """Calculate points for a reward event"""
        base_points = RewardService.POINTS_RULES.get(event_type, 0)
        
        if base_points <= 0:
            return 0
        
        # Check daily cap
        daily_cap = RewardService.DAILY_CAPS.get(event_type)
        if daily_cap:
            today = datetime.utcnow().date()
            today_events = db.query(RewardEvent).filter(
                RewardEvent.user_id == user_id,
                RewardEvent.event_type == event_type,
                RewardEvent.created_at >= datetime.combine(today, datetime.min.time())
            ).all()
            
            today_points = sum(event.points_earned for event in today_events)
            if today_points + base_points > daily_cap:
                return max(0, daily_cap - today_points)
        
        # Apply multipliers based on metadata
        multiplier = 1.0
        
        if event_type == "rental_completed" and metadata:
            # Bonus for longer rentals
            duration_hours = metadata.get("duration_hours", 0)
            if duration_hours >= 24:
                multiplier = 1.5
            elif duration_hours >= 8:
                multiplier = 1.2
        
        if event_type == "ride_completed" and metadata:
            # Bonus for EV rides
            if metadata.get("vehicle_type") in ["scooter", "bike"]:
                multiplier = 1.2
        
        return int(base_points * multiplier)
    
    @staticmethod
    def calculate_tier(points_balance: int) -> str:
        """Calculate user tier based on points balance"""
        for tier in ["platinum", "gold", "silver", "bronze"]:
            if points_balance >= RewardService.TIER_THRESHOLDS[tier]:
                return tier
        return "bronze"
    
    @staticmethod
    async def check_fraud(
        user_id: uuid.UUID,
        redemption_data: Any,
        db: Session
    ) -> Dict[str, Any]:
        """Check for fraudulent redemption patterns"""
        # Check for duplicate device redemptions
        recent_redemptions = db.query(RewardEvent).filter(
            RewardEvent.user_id == user_id,
            RewardEvent.event_type == "points_redeemed",
            RewardEvent.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        if recent_redemptions >= 5:
            return {
                "is_fraud": True,
                "reason": "Too many redemptions in short time"
            }
        
        # Check for suspicious point accumulation
        recent_events = db.query(RewardEvent).filter(
            RewardEvent.user_id == user_id,
            RewardEvent.created_at >= datetime.utcnow() - timedelta(days=1)
        ).all()
        
        daily_points = sum(event.points_earned for event in recent_events)
        if daily_points > 1000:  # Suspiciously high daily points
            return {
                "is_fraud": True,
                "reason": "Suspicious point accumulation pattern"
            }
        
        return {"is_fraud": False, "reason": None}