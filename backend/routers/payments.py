"""
Payments API routes
Handles Hyperswitch payment intents and webhooks
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid
import hmac
import hashlib

from database import get_db, User, Payment, Ride, Parcel, Rental, PaymentStatus, RideStatus, RentalStatus
from middleware.auth import get_current_active_user
from services.audit_service import AuditService
from services.payment_service import PaymentService
from schemas.payments import (
    PaymentIntentCreate, PaymentIntentResponse, 
    WebhookPayload, PaymentResponse
)

router = APIRouter()

@router.post("/intents", response_model=PaymentIntentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create payment intent for ride/parcel/rental"""
    # Validate entity exists and belongs to user
    entity = await PaymentService.validate_entity(
        db=db,
        entity_type=payment_data.entity_type,
        entity_id=payment_data.entity_id,
        user_id=current_user.id
    )
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{payment_data.entity_type.title()} not found"
        )
    
    # Create payment intent with Hyperswitch
    payment_intent = await PaymentService.create_payment_intent(
        amount=payment_data.amount,
        currency="INR",
        metadata={
            "user_id": str(current_user.id),
            "entity_type": payment_data.entity_type,
            "entity_id": str(payment_data.entity_id)
        }
    )
    
    # Create payment record
    payment = Payment(
        payment_intent_id=payment_intent["payment_intent_id"],
        user_id=current_user.id,
        entity_type=payment_data.entity_type,
        entity_id=payment_data.entity_id,
        amount=payment_data.amount,
        hyperswitch_data=payment_intent
    )
    
    db.add(payment)
    
    # Update entity with payment intent ID
    entity.payment_intent_id = payment_intent["payment_intent_id"]
    
    db.commit()
    db.refresh(payment)
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type="payment_intent_created",
        user_id=current_user.id,
        entity_type="payment",
        entity_id=payment.id,
        action="created",
        details={
            "payment_intent_id": payment_intent["payment_intent_id"],
            "amount": payment_data.amount,
            "entity_type": payment_data.entity_type,
            "entity_id": str(payment_data.entity_id)
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "payment_intent_id": payment_intent["payment_intent_id"],
        "client_secret": payment_intent.get("client_secret"),
        "amount": payment_data.amount,
        "currency": "INR",
        "status": "pending"
    }

@router.post("/webhooks", status_code=status.HTTP_200_OK)
async def handle_webhook(
    webhook_data: WebhookPayload,
    request: Request,
    x_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Handle Hyperswitch webhooks"""
    # Verify webhook signature
    if not PaymentService.verify_webhook_signature(
        payload=await request.body(),
        signature=x_signature
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    # Find payment record
    payment = db.query(Payment).filter(
        Payment.payment_intent_id == webhook_data.payment_intent_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Update payment status
    old_status = payment.status
    payment.status = PaymentService.map_hyperswitch_status(webhook_data.status)
    payment.hyperswitch_data = webhook_data.dict()
    payment.updated_at = datetime.utcnow()
    
    # Update entity status if payment succeeded
    if payment.status == PaymentStatus.COMPLETED:
        entity = await PaymentService.get_entity(
            db=db,
            entity_type=payment.entity_type,
            entity_id=payment.entity_id
        )
        
        if entity:
            if payment.entity_type in ["ride", "parcel"]:
                entity.status = RideStatus.PAID
            elif payment.entity_type == "rental":
                entity.status = RentalStatus.PAID
            elif payment.entity_type == "deposit":
                # Handle deposit payment
                rental = db.query(Rental).filter(Rental.id == payment.entity_id).first()
                if rental:
                    rental.deposit_payment_intent_id = payment.payment_intent_id
                    rental.status = RentalStatus.ACTIVE
            
            entity.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Log audit event
    await AuditService.log_event(
        correlation_id=webhook_data.payment_intent_id,  # Use payment intent as correlation ID
        event_type="payment_status_updated",
        user_id=payment.user_id,
        entity_type="payment",
        entity_id=payment.id,
        action="webhook_received",
        details={
            "old_status": old_status,
            "new_status": payment.status,
            "webhook_event": webhook_data.event_type,
            "entity_type": payment.entity_type,
            "entity_id": str(payment.entity_id)
        }
    )
    
    return {"message": "Webhook processed successfully"}

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get payment details"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Check authorization
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment"
        )
    
    return payment

@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    entity_type: Optional[str] = None,
    status_filter: Optional[PaymentStatus] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List user's payments"""
    query = db.query(Payment).filter(Payment.user_id == current_user.id)
    
    if entity_type:
        query = query.filter(Payment.entity_type == entity_type)
    
    if status_filter:
        query = query.filter(Payment.status == status_filter)
    
    payments = query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()
    return payments