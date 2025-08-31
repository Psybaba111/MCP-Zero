from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.reward import Reward, RewardEventType, RewardStatus, RewardRule
from app.models.user import User
from app.schemas.reward import (
    RewardEvent, RewardResponse, RewardBalance, RewardRedemption,
    RewardRedemptionResponse, RewardRule as RewardRuleSchema, RewardRuleResponse,
    RewardHistory, RewardTier, RewardLeaderboard
)
from app.services.audit_service import audit_service
from app.models.audit import AuditEventType

router = APIRouter()


@router.post("/events", response_model=RewardResponse)
async def create_reward_event(
    reward_data: RewardEvent,
    db: Session = Depends(get_db)
):
    """Create a new reward event and award points"""
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == reward_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get applicable reward rule
        rule = db.query(RewardRule).filter(
            RewardRule.event_type == reward_data.event_type,
            RewardRule.is_active == True
        ).order_by(RewardRule.priority.desc()).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No reward rule found for this event type"
            )
        
        # Check daily and monthly caps
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
        
        # Check daily cap
        if rule.daily_cap:
            daily_points = db.query(Reward).filter(
                Reward.user_id == reward_data.user_id,
                Reward.event_type == reward_data.event_type,
                Reward.created_at >= today
            ).with_entities(db.func.sum(Reward.points_earned)).scalar() or 0
            
            if daily_points + reward_data.points_earned > rule.daily_cap:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Daily reward cap exceeded"
                )
        
        # Check monthly cap
        if rule.monthly_cap:
            monthly_points = db.query(Reward).filter(
                Reward.user_id == reward_data.user_id,
                Reward.event_type == reward_data.event_type,
                Reward.created_at >= month_start
            ).with_entities(db.func.sum(Reward.points_earned)).scalar() or 0
            
            if monthly_points + reward_data.points_earned > rule.monthly_cap:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Monthly reward cap exceeded"
                )
        
        # Calculate current balance
        current_balance = db.query(Reward).filter(
            Reward.user_id == reward_data.user_id,
            Reward.status == RewardStatus.ACCRUED
        ).with_entities(db.func.sum(Reward.points_earned)).scalar() or 0
        
        # Create reward record
        new_reward = Reward(
            user_id=reward_data.user_id,
            event_type=reward_data.event_type,
            event_id=reward_data.event_id,
            event_metadata=reward_data.event_metadata,
            points_earned=reward_data.points_earned,
            points_balance=current_balance + reward_data.points_earned,
            status=RewardStatus.ACCRUED,
            rule_applied=rule.id,
            daily_cap=rule.daily_cap,
            monthly_cap=rule.monthly_cap,
            expires_at=datetime.utcnow() + timedelta(days=365)  # 1 year expiry
        )
        
        db.add(new_reward)
        db.commit()
        db.refresh(new_reward)
        
        # Log reward event
        await audit_service.log_event(
            event_type=AuditEventType.AUTOMATION_TRIGGERED,
            user_id=reward_data.user_id,
            reward_id=new_reward.id,
            event_data={
                "event_type": reward_data.event_type,
                "points_earned": reward_data.points_earned,
                "rule_applied": rule.id
            },
            source="rewards_service",
            tags=["rewards", "points"]
        )
        
        return new_reward
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reward event: {str(e)}"
        )


@router.get("/{reward_id}", response_model=RewardResponse)
async def get_reward(
    reward_id: int,
    db: Session = Depends(get_db)
):
    """Get reward details by ID"""
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward not found"
        )
    return reward


@router.get("/user/{user_id}/balance", response_model=RewardBalance)
async def get_user_reward_balance(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user's reward balance and tier information"""
    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Calculate reward statistics
    total_points = db.query(Reward).filter(
        Reward.user_id == user_id
    ).with_entities(db.func.sum(Reward.points_earned)).scalar() or 0
    
    available_points = db.query(Reward).filter(
        Reward.user_id == user_id,
        Reward.status == RewardStatus.ACCRUED,
        Reward.is_expired == False
    ).with_entities(db.func.sum(Reward.points_earned)).scalar() or 0
    
    expired_points = db.query(Reward).filter(
        Reward.user_id == user_id,
        Reward.is_expired == True
    ).with_entities(db.func.sum(Reward.points_earned)).scalar() or 0
    
    # Determine tier based on total points
    if total_points >= 10000:
        tier = "Platinum"
        next_tier = None
        points_to_next_tier = 0
        tier_benefits = ["50% bonus on all rewards", "Priority support", "Exclusive offers"]
    elif total_points >= 5000:
        tier = "Gold"
        next_tier = "Platinum"
        points_to_next_tier = 10000 - total_points
        tier_benefits = ["25% bonus on all rewards", "Priority support"]
    elif total_points >= 1000:
        tier = "Silver"
        next_tier = "Gold"
        points_to_next_tier = 5000 - total_points
        tier_benefits = ["10% bonus on all rewards"]
    else:
        tier = "Bronze"
        next_tier = "Silver"
        points_to_next_tier = 1000 - total_points
        tier_benefits = ["Standard rewards"]
    
    return RewardBalance(
        user_id=user_id,
        total_points=total_points,
        available_points=available_points,
        expired_points=expired_points,
        tier=tier,
        next_tier=next_tier,
        points_to_next_tier=points_to_next_tier,
        tier_benefits=tier_benefits
    )


@router.post("/redeem", response_model=RewardRedemptionResponse)
async def redeem_rewards(
    redemption_data: RewardRedemption,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Redeem rewards for cashback, discounts, or vouchers"""
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user has enough points
        available_points = db.query(Reward).filter(
            Reward.user_id == user_id,
            Reward.status == RewardStatus.ACCRUED,
            Reward.is_expired == False
        ).with_entities(db.func.sum(Reward.points_earned)).scalar() or 0
        
        if available_points < redemption_data.points_to_redeem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient points for redemption"
            )
        
        # Calculate redemption value (1 point = ₹0.01)
        redemption_value = redemption_data.points_to_redeem * 0.01
        
        # Generate redemption ID
        redemption_id = f"red_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Mark points as redeemed
        # In real app, this would be more sophisticated point allocation
        rewards_to_redeem = db.query(Reward).filter(
            Reward.user_id == user_id,
            Reward.status == RewardStatus.ACCRUED,
            Reward.is_expired == False
        ).limit(redemption_data.points_to_redeem // 100 + 1).all()
        
        points_redeemed = 0
        for reward in rewards_to_redeem:
            if points_redeemed >= redemption_data.points_to_redeem:
                break
            
            points_to_redeem_from_reward = min(
                reward.points_earned, 
                redemption_data.points_to_redeem - points_redeemed
            )
            
            reward.status = RewardStatus.REDEEMED
            reward.redeemed_at = datetime.utcnow()
            reward.redemption_amount = points_to_redeem_from_reward * 0.01
            reward.redemption_currency = "inr"
            
            points_redeemed += points_to_redeem_from_reward
        
        db.commit()
        
        # Log redemption
        await audit_service.log_event(
            event_type=AuditEventType.AUTOMATION_TRIGGERED,
            user_id=user_id,
            event_data={
                "redemption_id": redemption_id,
                "points_redeemed": redemption_data.points_to_redeem,
                "redemption_value": redemption_value,
                "redemption_type": redemption_data.redemption_type
            },
            source="rewards_service",
            tags=["rewards", "redemption"]
        )
        
        return RewardRedemptionResponse(
            redemption_id=redemption_id,
            points_redeemed=redemption_data.points_to_redeem,
            redemption_type=redemption_data.redemption_type,
            redemption_value=redemption_value,
            currency="INR",
            status="processed",
            processed_at=datetime.utcnow(),
            message="Rewards redeemed successfully"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to redeem rewards: {str(e)}"
        )


@router.get("/rules", response_model=List[RewardRuleResponse])
async def get_reward_rules(
    event_type: Optional[RewardEventType] = None,
    db: Session = Depends(get_db)
):
    """Get reward rules configuration"""
    query = db.query(RewardRule).filter(RewardRule.is_active == True)
    
    if event_type:
        query = query.filter(RewardRule.event_type == event_type)
    
    rules = query.order_by(RewardRule.priority.desc()).all()
    return rules


@router.post("/rules", response_model=RewardRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_reward_rule(
    rule_data: RewardRuleSchema,
    db: Session = Depends(get_db)
):
    """Create a new reward rule"""
    try:
        new_rule = RewardRule(
            event_type=rule_data.event_type,
            points_per_event=rule_data.points_per_event,
            daily_cap=rule_data.daily_cap,
            weekly_cap=rule_data.weekly_cap,
            monthly_cap=rule_data.monthly_cap,
            min_amount=rule_data.min_amount,
            max_amount=rule_data.max_amount,
            conditions=rule_data.conditions,
            is_active=rule_data.is_active,
            priority=rule_data.priority
        )
        
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        
        return new_rule
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reward rule: {str(e)}"
        )


@router.get("/user/{user_id}/history", response_model=RewardHistory)
async def get_user_reward_history(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get user's reward history"""
    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get reward events
    events = db.query(Reward).filter(
        Reward.user_id == user_id
    ).order_by(Reward.created_at.desc()).offset(skip).limit(limit).all()
    
    # Get redemptions (simplified - in real app, this would be a separate table)
    redemptions = []
    
    # Calculate totals
    total_events = len(events)
    total_points_earned = sum([e.points_earned for e in events])
    total_points_redeemed = sum([e.redemption_amount * 100 for e in events if e.redemption_amount])
    
    return RewardHistory(
        user_id=user_id,
        total_events=total_events,
        total_points_earned=total_points_earned,
        total_points_redeemed=total_points_redeemed,
        events=events,
        redemptions=redemptions
    )


@router.get("/tiers", response_model=List[RewardTier])
async def get_reward_tiers():
    """Get available reward tiers"""
    return [
        RewardTier(
            tier_name="Bronze",
            min_points=0,
            max_points=999,
            benefits=["Standard rewards", "Basic support"],
            icon="bronze-icon",
            color="#CD7F32"
        ),
        RewardTier(
            tier_name="Silver",
            min_points=1000,
            max_points=4999,
            benefits=["10% bonus on all rewards", "Priority support"],
            icon="silver-icon",
            color="#C0C0C0"
        ),
        RewardTier(
            tier_name="Gold",
            min_points=5000,
            max_points=9999,
            benefits=["25% bonus on all rewards", "Priority support", "Exclusive offers"],
            icon="gold-icon",
            color="#FFD700"
        ),
        RewardTier(
            tier_name="Platinum",
            min_points=10000,
            max_points=None,
            benefits=["50% bonus on all rewards", "Priority support", "Exclusive offers", "VIP treatment"],
            icon="platinum-icon",
            color="#E5E4E2"
        )
    ]


@router.get("/leaderboard", response_model=List[RewardLeaderboard])
async def get_reward_leaderboard(
    period: str = "monthly",  # "weekly", "monthly", "all_time"
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get reward leaderboard"""
    # Calculate date range based on period
    now = datetime.utcnow()
    if period == "weekly":
        start_date = now - timedelta(days=7)
    elif period == "monthly":
        start_date = now.replace(day=1)
    else:
        start_date = datetime.min
    
    # Get top users by points earned in the period
    # This is a simplified query - in real app, would be more optimized
    top_users = db.query(
        User.id,
        User.full_name,
        db.func.sum(Reward.points_earned).label("total_points")
    ).join(Reward, User.id == Reward.user_id).filter(
        Reward.created_at >= start_date
    ).group_by(User.id, User.full_name).order_by(
        db.func.sum(Reward.points_earned).desc()
    ).limit(limit).all()
    
    # Calculate tier and additional stats for each user
    leaderboard = []
    for rank, (user_id, user_name, total_points) in enumerate(top_users, 1):
        # Determine tier
        if total_points >= 10000:
            tier = "Platinum"
        elif total_points >= 5000:
            tier = "Gold"
        elif total_points >= 1000:
            tier = "Silver"
        else:
            tier = "Bronze"
        
        # Calculate period-specific points
        if period == "weekly":
            period_points = db.query(Reward).filter(
                Reward.user_id == user_id,
                Reward.created_at >= start_date
            ).with_entities(db.func.sum(Reward.points_earned)).scalar() or 0
        elif period == "monthly":
            period_points = db.query(Reward).filter(
                Reward.user_id == user_id,
                Reward.created_at >= start_date
            ).with_entities(db.func.sum(Reward.points_earned)).scalar() or 0
        else:
            period_points = total_points
        
        leaderboard.append(RewardLeaderboard(
            user_id=user_id,
            user_name=user_name,
            total_points=total_points,
            tier=tier,
            rank=rank,
            monthly_points=period_points if period == "monthly" else 0,
            weekly_points=period_points if period == "weekly" else 0
        ))
    
    return leaderboard


@router.get("/", response_model=List[RewardResponse])
async def list_rewards(
    user_id: Optional[int] = None,
    event_type: Optional[RewardEventType] = None,
    status: Optional[RewardStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List rewards with filters"""
    query = db.query(Reward)
    
    if user_id:
        query = query.filter(Reward.user_id == user_id)
    if event_type:
        query = query.filter(Reward.event_type == event_type)
    if status:
        query = query.filter(Reward.status == status)
    
    rewards = query.order_by(Reward.created_at.desc()).offset(skip).limit(limit).all()
    return rewards