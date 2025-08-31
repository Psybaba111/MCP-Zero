"""
Webhook Integration for EV Platform Backend
Connects backend events to Rube.app workflows
"""

from fastapi import APIRouter, Request, BackgroundTasks
import httpx
import asyncio
from typing import Dict, Any
import os

router = APIRouter()

# Rube webhook URLs (configured after deployment)
RUBE_WEBHOOKS = {
    "kyc_document_uploaded": os.getenv("RUBE_KYC_WEBHOOK_URL"),
    "rental_returned": os.getenv("RUBE_DEPOSIT_WEBHOOK_URL"),
    "ride_payment_completed": os.getenv("RUBE_RIDE_WEBHOOK_URL"),
    "license_expiry_check": os.getenv("RUBE_LICENSE_WEBHOOK_URL")
}

class RubeIntegration:
    """Integration service for Rube.app workflows"""
    
    @staticmethod
    async def trigger_workflow(webhook_url: str, payload: Dict[str, Any]) -> bool:
        """Trigger a Rube workflow via webhook"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    timeout=30.0,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"Failed to trigger Rube workflow: {e}")
            return False
    
    @staticmethod
    async def trigger_kyc_workflow(user_id: str, document_id: str, document_url: str, document_type: str):
        """Trigger KYC approval workflow"""
        webhook_url = RUBE_WEBHOOKS.get("kyc_document_uploaded")
        if not webhook_url:
            print("KYC webhook URL not configured")
            return False
        
        payload = {
            "event_type": "kyc_document_uploaded",
            "user_id": user_id,
            "document_id": document_id,
            "document_url": document_url,
            "document_type": document_type,
            "timestamp": datetime.now().isoformat()
        }
        
        return await RubeIntegration.trigger_workflow(webhook_url, payload)
    
    @staticmethod
    async def trigger_deposit_release(rental_id: str, user_id: str):
        """Trigger deposit release workflow"""
        webhook_url = RUBE_WEBHOOKS.get("rental_returned")
        if not webhook_url:
            print("Deposit release webhook URL not configured")
            return False
        
        payload = {
            "event_type": "rental_returned",
            "rental_id": rental_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        return await RubeIntegration.trigger_workflow(webhook_url, payload)
    
    @staticmethod
    async def trigger_ride_assignment(entity_id: str, entity_type: str):
        """Trigger ride assignment workflow"""
        webhook_url = RUBE_WEBHOOKS.get("ride_payment_completed")
        if not webhook_url:
            print("Ride assignment webhook URL not configured")
            return False
        
        payload = {
            "event_type": "ride_payment_completed",
            "entity_id": entity_id,
            "entity_type": entity_type,
            "timestamp": datetime.now().isoformat()
        }
        
        return await RubeIntegration.trigger_workflow(webhook_url, payload)

# Webhook endpoints for triggering Rube workflows
@router.post("/rube/kyc-uploaded")
async def trigger_kyc_workflow(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Trigger KYC workflow when document is uploaded"""
    data = await request.json()
    
    background_tasks.add_task(
        RubeIntegration.trigger_kyc_workflow,
        data["user_id"],
        data["document_id"], 
        data["document_url"],
        data["document_type"]
    )
    
    return {"message": "KYC workflow triggered", "status": "success"}

@router.post("/rube/rental-returned")
async def trigger_deposit_workflow(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Trigger deposit release workflow when vehicle is returned"""
    data = await request.json()
    
    background_tasks.add_task(
        RubeIntegration.trigger_deposit_release,
        data["rental_id"],
        data["user_id"]
    )
    
    return {"message": "Deposit release workflow triggered", "status": "success"}

@router.post("/rube/payment-completed")
async def trigger_assignment_workflow(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Trigger ride assignment workflow when payment is completed"""
    data = await request.json()
    
    background_tasks.add_task(
        RubeIntegration.trigger_ride_assignment,
        data["entity_id"],
        data["entity_type"]
    )
    
    return {"message": "Ride assignment workflow triggered", "status": "success"}

@router.get("/rube/status")
async def get_rube_status():
    """Get status of Rube integration"""
    configured_webhooks = {
        name: url is not None 
        for name, url in RUBE_WEBHOOKS.items()
    }
    
    return {
        "rube_integration": "active",
        "configured_webhooks": configured_webhooks,
        "total_workflows": len(RUBE_WEBHOOKS),
        "timestamp": datetime.now().isoformat()
    }