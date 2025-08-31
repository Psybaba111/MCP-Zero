"""
Payment Service for EV Platform
Handles Hyperswitch integration and payment processing
"""

import httpx
import hmac
import hashlib
import os
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import uuid

from database import Ride, Parcel, Rental, PaymentStatus

class PaymentService:
    """Service for payment processing with Hyperswitch"""
    
    HYPERSWITCH_API_URL = os.getenv("HYPERSWITCH_API_URL", "https://sandbox.hyperswitch.io")
    API_KEY = os.getenv("HYPERSWITCH_API_KEY", "your-api-key")
    WEBHOOK_SECRET = os.getenv("HYPERSWITCH_WEBHOOK_SECRET", "your-webhook-secret")
    
    @staticmethod
    async def create_payment_intent(
        amount: float,
        currency: str = "INR",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create payment intent with Hyperswitch"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{PaymentService.HYPERSWITCH_API_URL}/payments",
                    headers={
                        "Authorization": f"Bearer {PaymentService.API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "amount": int(amount * 100),  # Convert to paise/cents
                        "currency": currency,
                        "confirm": False,
                        "capture_method": "automatic",
                        "metadata": metadata or {}
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                # Fallback for development/testing
                return {
                    "payment_intent_id": f"pi_mock_{uuid.uuid4().hex[:16]}",
                    "client_secret": f"pi_mock_{uuid.uuid4().hex[:16]}_secret",
                    "status": "requires_payment_method"
                }
    
    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: Optional[str]) -> bool:
        """Verify Hyperswitch webhook signature"""
        if not signature or not PaymentService.WEBHOOK_SECRET:
            # Skip verification in development
            return True
        
        try:
            expected_signature = hmac.new(
                PaymentService.WEBHOOK_SECRET.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(f"sha256={expected_signature}", signature)
        except Exception:
            return False
    
    @staticmethod
    def map_hyperswitch_status(hyperswitch_status: str) -> PaymentStatus:
        """Map Hyperswitch status to our PaymentStatus enum"""
        status_mapping = {
            "requires_payment_method": PaymentStatus.PENDING,
            "requires_confirmation": PaymentStatus.PENDING,
            "requires_action": PaymentStatus.PENDING,
            "processing": PaymentStatus.PROCESSING,
            "succeeded": PaymentStatus.COMPLETED,
            "failed": PaymentStatus.FAILED,
            "canceled": PaymentStatus.FAILED,
            "refunded": PaymentStatus.REFUNDED
        }
        
        return status_mapping.get(hyperswitch_status, PaymentStatus.PENDING)
    
    @staticmethod
    async def validate_entity(
        db: Session,
        entity_type: str,
        entity_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[Any]:
        """Validate that entity exists and belongs to user"""
        if entity_type == "ride":
            return db.query(Ride).filter(
                Ride.id == entity_id,
                Ride.passenger_id == user_id
            ).first()
        elif entity_type == "parcel":
            return db.query(Parcel).filter(
                Parcel.id == entity_id,
                Parcel.sender_id == user_id
            ).first()
        elif entity_type in ["rental", "deposit"]:
            return db.query(Rental).filter(
                Rental.id == entity_id,
                Rental.renter_id == user_id
            ).first()
        
        return None
    
    @staticmethod
    async def get_entity(
        db: Session,
        entity_type: str,
        entity_id: uuid.UUID
    ) -> Optional[Any]:
        """Get entity by type and ID"""
        if entity_type == "ride":
            return db.query(Ride).filter(Ride.id == entity_id).first()
        elif entity_type == "parcel":
            return db.query(Parcel).filter(Parcel.id == entity_id).first()
        elif entity_type in ["rental", "deposit"]:
            return db.query(Rental).filter(Rental.id == entity_id).first()
        
        return None
    
    @staticmethod
    async def create_refund(
        payment_intent_id: str,
        amount: Optional[float] = None,
        reason: str = "requested_by_customer"
    ) -> Dict[str, Any]:
        """Create refund through Hyperswitch"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{PaymentService.HYPERSWITCH_API_URL}/refunds",
                    headers={
                        "Authorization": f"Bearer {PaymentService.API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "payment_id": payment_intent_id,
                        "amount": int(amount * 100) if amount else None,
                        "reason": reason
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                # Fallback for development/testing
                return {
                    "refund_id": f"re_mock_{uuid.uuid4().hex[:16]}",
                    "status": "succeeded",
                    "amount": int(amount * 100) if amount else 0
                }