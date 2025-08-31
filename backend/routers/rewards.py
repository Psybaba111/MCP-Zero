"""
Rewards API routes
Handles points system, events, and redemptions
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db, User, RewardAccount, RewardEvent
from middleware.auth import get_current_active_user
from services.audit_service import AuditService
from services.reward_service import RewardService
from schemas.rewards import (
    RewardEventCreate, RewardEventResponse,
    RewardAccountResponse, RedemptionRequest, RedemptionResponse
)

router = APIRouter()

@router.post("/events", response_model=RewardEventResponse, status_code=status.HTTP_201_CREATED)
async def create_reward_event(
    event_data: RewardEventCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process reward event and accrue points"""
    # Calculate points based on event type and rules
    points_earned = await RewardService.calculate_points(
        event_type=event_data.event_type,
        metadata=event_data.metadata,
        user_id=current_user.id,
        db=db
    )
    
    if points_earned <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No points earned for this event"
        )
    
    # Create reward event
    reward_event = RewardEvent(
        user_id=current_user.id,
        event_type=event_data.event_type,
        points_earned=points_earned,
        entity_type=event_data.entity_type,
        entity_id=event_data.entity_id,
        metadata=event_data.metadata
    )
    
    db.add(reward_event)
    
    # Update or create reward account
    reward_account = db.query(RewardAccount).filter(
        RewardAccount.user_id == current_user.id
    ).first()
    
    if not reward_account:
        reward_account = RewardAccount(
            user_id=current_user.id,
            points_balance=points_earned
        )
        db.add(reward_account)
    else:
        reward_account.points_balance += points_earned
        reward_account.updated_at = datetime.utcnow()
    
    # Update tier if needed
    new_tier = RewardService.calculate_tier(reward_account.points_balance)
    if new_tier != reward_account.tier:
        reward_account.tier = new_tier
    
    db.commit()
    db.refresh(reward_event)
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="reward_points_earned",
        user_id=current_user.id,
        entity_type="reward_event",
        entity_id=reward_event.id,
        action="points_accrued",
        details={
            "event_type": event_data.event_type,
            "points_earned": points_earned,
            "new_balance": reward_account.points_balance,
            "new_tier": reward_account.tier
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return reward_event

@router.get("/balance", response_model=RewardAccountResponse)
async def get_reward_balance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's reward balance and tier"""
    reward_account = db.query(RewardAccount).filter(
        RewardAccount.user_id == current_user.id
    ).first()
    
    if not reward_account:
        # Create default account
        reward_account = RewardAccount(user_id=current_user.id)
        db.add(reward_account)
        db.commit()
        db.refresh(reward_account)
    
    return reward_account

@router.post("/redeem", response_model=RedemptionResponse, status_code=status.HTTP_201_CREATED)
async def redeem_points(
    redemption_data: RedemptionRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Redeem reward points"""
    reward_account = db.query(RewardAccount).filter(
        RewardAccount.user_id == current_user.id
    ).first()
    
    if not reward_account or reward_account.points_balance < redemption_data.points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient points balance"
        )
    
    # Check for fraud (duplicate device, suspicious patterns)
    fraud_check = await RewardService.check_fraud(
        user_id=current_user.id,
        redemption_data=redemption_data,
        db=db
    )
    
    if fraud_check["is_fraud"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Redemption blocked: {fraud_check['reason']}"
        )
    
    # Process redemption
    reward_account.points_balance -= redemption_data.points
    reward_account.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="reward_points_redeemed",
        user_id=current_user.id,
        entity_type="reward_account",
        entity_id=reward_account.id,
        action="points_redeemed",
        details={
            "points_redeemed": redemption_data.points,
            "redemption_type": redemption_data.redemption_type,
            "new_balance": reward_account.points_balance
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "success": True,
        "points_redeemed": redemption_data.points,
        "new_balance": reward_account.points_balance,
        "redemption_id": str(uuid.uuid4())
    }

@router.get("/events", response_model=List[RewardEventResponse])
async def get_reward_events(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's reward events history"""
    events = db.query(RewardEvent).filter(
        RewardEvent.user_id == current_user.id
    ).order_by(RewardEvent.created_at.desc()).offset(offset).limit(limit).all()
    
    return events