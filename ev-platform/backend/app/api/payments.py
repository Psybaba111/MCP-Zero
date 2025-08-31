from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from app.db.database import get_db
from app.models.payment import Payment, PaymentType, PaymentStatus, PaymentMethod
from app.models.ride import Ride
from app.models.rental import Rental
from app.models.user import User
from app.schemas.payment import (
    PaymentIntentCreate, PaymentIntentResponse, HyperswitchWebhook,
    PaymentResponse, RefundRequest, RefundResponse,
    DepositHold, DepositRelease, PaymentMethodResponse, PaymentSummary
)
from app.services.audit_service import audit_service
from app.models.audit import AuditEventType
from app.core.config import settings

router = APIRouter()


@router.post("/intents", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    db: Session = Depends(get_db)
):
    """Create a payment intent with Hyperswitch"""
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == payment_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate related entity exists
        if payment_data.ride_id:
            ride = db.query(Ride).filter(Ride.id == payment_data.ride_id).first()
            if not ride:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ride not found"
                )
        
        if payment_data.rental_id:
            rental = db.query(Rental).filter(Rental.id == payment_data.rental_id).first()
            if not rental:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Rental not found"
                )
        
        # Generate payment intent ID (in real app, this would come from Hyperswitch)
        payment_intent_id = f"pi_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{payment_data.user_id}"
        client_secret = f"cs_{payment_intent_id}"
        
        # Create payment record
        new_payment = Payment(
            payment_intent_id=payment_intent_id,
            client_secret=client_secret,
            amount=payment_data.amount,
            currency=payment_data.currency,
            payment_type=payment_data.payment_type,
            ride_id=payment_data.ride_id,
            rental_id=payment_data.rental_id,
            user_id=payment_data.user_id,
            description=payment_data.description,
            metadata=payment_data.metadata,
            status=PaymentStatus.PENDING
        )
        
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
        
        # Log payment intent creation
        await audit_service.log_payment_event(
            payment_id=new_payment.id,
            event_type=AuditEventType.PAYMENT_CREATED,
            user_id=payment_data.user_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            status="pending"
        )
        
        return PaymentIntentResponse(
            payment_intent_id=payment_intent_id,
            client_secret=client_secret,
            amount=payment_data.amount,
            currency=payment_data.currency,
            status=PaymentStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment intent: {str(e)}"
        )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """Get payment details by ID"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment


@router.post("/webhook/hyperswitch")
async def hyperswitch_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Hyperswitch webhook notifications"""
    try:
        # Verify webhook signature (in real app, verify with Hyperswitch)
        # signature = request.headers.get("x-hyperswitch-signature")
        # if not verify_signature(request.body, signature, settings.HYPERSWITCH_WEBHOOK_SECRET):
        #     raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Parse webhook data
        webhook_data = await request.json()
        
        # Extract payment information
        payment_intent_id = webhook_data.get("payment_intent_id")
        status = webhook_data.get("status")
        amount = webhook_data.get("amount")
        currency = webhook_data.get("currency")
        
        # Find payment record
        payment = db.query(Payment).filter(Payment.payment_intent_id == payment_intent_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment intent not found"
            )
        
        # Update payment status
        if status == "succeeded":
            payment.status = PaymentStatus.SUCCEEDED
            payment.succeeded_at = datetime.utcnow()
            payment.hyperswitch_response = webhook_data
            
            # Update related entity status
            if payment.ride_id:
                ride = db.query(Ride).filter(Ride.id == payment.ride_id).first()
                if ride:
                    ride.payment_status = "paid"
                    ride.payment_intent_id = payment_intent_id
            
            if payment.rental_id:
                rental = db.query(Rental).filter(Rental.id == payment.rental_id).first()
                if rental:
                    rental.payment_status = "paid"
                    rental.payment_intent_id = payment_intent_id
                    
        elif status == "failed":
            payment.status = PaymentStatus.FAILED
            payment.failed_at = datetime.utcnow()
            payment.error_code = webhook_data.get("error_code")
            payment.error_message = webhook_data.get("error_message")
            payment.hyperswitch_response = webhook_data
        
        db.commit()
        db.refresh(payment)
        
        # Log webhook receipt
        await audit_service.log_event(
            event_type=AuditEventType.WEBHOOK_RECEIVED,
            event_id=payment_intent_id,
            user_id=payment.user_id,
            event_data={"webhook_data": webhook_data, "payment_id": payment.id},
            source="hyperswitch_webhook",
            tags=["webhook", "payment"]
        )
        
        # Log payment status update
        await audit_service.log_payment_event(
            payment_id=payment.id,
            event_type=AuditEventType.PAYMENT_SUCCEEDED if status == "succeeded" else AuditEventType.PAYMENT_FAILED,
            user_id=payment.user_id,
            amount=amount,
            currency=currency,
            status=status
        )
        
        return {"status": "success", "message": "Webhook processed successfully"}
        
    except Exception as e:
        # Log webhook error
        await audit_service.log_event(
            event_type=AuditEventType.ERROR_OCCURRED,
            event_data={"error": str(e), "webhook_data": webhook_data if 'webhook_data' in locals() else None},
            source="hyperswitch_webhook",
            severity="error",
            tags=["webhook", "payment", "error"]
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )


@router.post("/{payment_id}/refund", response_model=RefundResponse)
async def refund_payment(
    payment_id: int,
    refund_data: RefundRequest,
    db: Session = Depends(get_db)
):
    """Process a payment refund"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != PaymentStatus.SUCCEEDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refund successful payments"
        )
    
    # Calculate refund amount
    refund_amount = refund_data.amount if refund_data.amount else payment.amount
    
    if refund_amount > payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund amount cannot exceed payment amount"
        )
    
    # Process refund (in real app, this would call Hyperswitch API)
    refund_id = f"ref_{payment_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    # Update payment record
    payment.refund_amount = refund_amount
    payment.refund_reason = refund_data.reason
    payment.refund_processed_at = datetime.utcnow()
    payment.status = PaymentStatus.REFUNDED
    
    db.commit()
    db.refresh(payment)
    
    # Log refund
    await audit_service.log_payment_event(
        payment_id=payment.id,
        event_type=AuditEventType.PAYMENT_REFUNDED,
        user_id=payment.user_id,
        amount=refund_amount,
        currency=payment.currency,
        status="refunded",
        metadata={"refund_id": refund_id, "reason": refund_data.reason}
    )
    
    return RefundResponse(
        refund_id=refund_id,
        payment_id=payment.id,
        amount=refund_amount,
        status="processed",
        reason=refund_data.reason,
        processed_at=payment.refund_processed_at,
        message="Refund processed successfully"
    )


@router.post("/deposits/hold")
async def hold_deposit(
    deposit_data: DepositHold,
    db: Session = Depends(get_db)
):
    """Hold a deposit for a rental"""
    try:
        # Validate rental exists
        rental = db.query(Rental).filter(Rental.id == deposit_data.rental_id).first()
        if not rental:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rental not found"
            )
        
        # Create deposit hold payment
        deposit_payment = Payment(
            payment_intent_id=f"dep_{deposit_data.rental_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            amount=deposit_data.amount,
            currency=deposit_data.currency,
            payment_type=PaymentType.DEPOSIT,
            rental_id=deposit_data.rental_id,
            user_id=rental.renter_id,
            description=deposit_data.description,
            status=PaymentStatus.SUCCEEDED,
            succeeded_at=datetime.utcnow()
        )
        
        db.add(deposit_payment)
        
        # Update rental deposit status
        rental.deposit_held = True
        
        db.commit()
        db.refresh(deposit_payment)
        
        # Log deposit hold
        await audit_service.log_payment_event(
            payment_id=deposit_payment.id,
            event_type=AuditEventType.PAYMENT_SUCCEEDED,
            user_id=rental.renter_id,
            amount=deposit_data.amount,
            currency=deposit_data.currency,
            status="deposit_held"
        )
        
        return {"message": "Deposit held successfully", "payment_id": deposit_payment.id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to hold deposit: {str(e)}"
        )


@router.post("/deposits/release")
async def release_deposit(
    deposit_data: DepositRelease,
    db: Session = Depends(get_db)
):
    """Release a held deposit"""
    try:
        # Find the deposit payment
        deposit_payment = db.query(Payment).filter(
            Payment.rental_id == deposit_data.rental_id,
            Payment.payment_type == PaymentType.DEPOSIT,
            Payment.status == PaymentStatus.SUCCEEDED
        ).first()
        
        if not deposit_payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deposit payment not found"
            )
        
        # Calculate release amount
        release_amount = deposit_data.amount
        if deposit_data.partial_deduction:
            release_amount = deposit_data.amount - deposit_data.partial_deduction
        
        # Create refund record
        deposit_payment.refund_amount = release_amount
        deposit_payment.refund_reason = deposit_data.reason
        deposit_payment.refund_processed_at = datetime.utcnow()
        deposit_payment.status = PaymentStatus.REFUNDED
        
        # Update rental
        rental = db.query(Rental).filter(Rental.id == deposit_data.rental_id).first()
        if rental:
            rental.deposit_released = True
            rental.deposit_released_at = datetime.utcnow()
        
        db.commit()
        
        # Log deposit release
        await audit_service.log_payment_event(
            payment_id=deposit_payment.id,
            event_type=AuditEventType.PAYMENT_REFUNDED,
            user_id=deposit_payment.user_id,
            amount=release_amount,
            currency=deposit_payment.currency,
            status="deposit_released",
            metadata={"reason": deposit_data.reason, "partial_deduction": deposit_data.partial_deduction}
        )
        
        return {"message": "Deposit released successfully", "amount": release_amount}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to release deposit: {str(e)}"
        )


@router.get("/methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods():
    """Get available payment methods"""
    return [
        PaymentMethodResponse(
            type=PaymentMethod.UPI,
            display_name="UPI",
            icon="upi-icon",
            is_available=True,
            processing_fee=0.0
        ),
        PaymentMethodResponse(
            type=PaymentMethod.CARD,
            display_name="Credit/Debit Card",
            icon="card-icon",
            is_available=True,
            processing_fee=2.0
        ),
        PaymentMethodResponse(
            type=PaymentMethod.NETBANKING,
            display_name="Net Banking",
            icon="netbanking-icon",
            is_available=True,
            processing_fee=0.0
        ),
        PaymentMethodResponse(
            type=PaymentMethod.WALLET,
            display_name="Digital Wallet",
            icon="wallet-icon",
            is_available=True,
            processing_fee=1.0
        )
    ]


@router.get("/user/{user_id}/summary", response_model=PaymentSummary)
async def get_user_payment_summary(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get payment summary for a specific user"""
    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user's payments
    user_payments = db.query(Payment).filter(Payment.user_id == user_id).all()
    
    # Calculate summary statistics
    total_payments = len(user_payments)
    successful_payments = len([p for p in user_payments if p.status == PaymentStatus.SUCCEEDED])
    failed_payments = len([p for p in user_payments if p.status == PaymentStatus.FAILED])
    total_amount = sum([p.amount for p in user_payments if p.status == PaymentStatus.SUCCEEDED])
    
    # Get available payment methods
    payment_methods = await get_payment_methods()
    
    return PaymentSummary(
        total_payments=total_payments,
        successful_payments=successful_payments,
        failed_payments=failed_payments,
        total_amount=total_amount,
        currency="INR",
        payment_methods=payment_methods
    )


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    user_id: Optional[int] = None,
    status: Optional[PaymentStatus] = None,
    payment_type: Optional[PaymentType] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List payments with filters"""
    query = db.query(Payment)
    
    if user_id:
        query = query.filter(Payment.user_id == user_id)
    if status:
        query = query.filter(Payment.status == status)
    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)
    
    payments = query.offset(skip).limit(limit).all()
    return payments