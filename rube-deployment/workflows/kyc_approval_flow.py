"""
KYC Approval Flow for Rube.app
Automated KYC document processing with intelligent tool discovery
"""

from composio import Composio, Action
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

class KYCApprovalFlow:
    def __init__(self):
        self.composio = Composio()
        
    async def process_kyc_document(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main KYC processing workflow
        Triggered when a user uploads a KYC document
        """
        try:
            user_id = webhook_data.get("user_id")
            document_id = webhook_data.get("document_id")
            document_url = webhook_data.get("document_url")
            document_type = webhook_data.get("document_type")
            
            # Step 1: Extract document data using AI/OCR
            extraction_result = await self.extract_document_data(
                document_url, document_type
            )
            
            # Step 2: Validate extracted data
            validation_result = await self.validate_document_data(
                extraction_result, document_type
            )
            
            # Step 3: Auto-approve or flag for manual review
            if validation_result["is_valid"] and extraction_result["confidence"] > 0.85:
                approval_result = await self.auto_approve_document(
                    user_id, document_id, extraction_result["data"]
                )
                await self.notify_auto_approval(user_id, document_type)
            else:
                await self.flag_for_manual_review(
                    user_id, document_id, document_type, 
                    validation_result["errors"], extraction_result["confidence"]
                )
            
            # Step 4: Log to audit and Notion
            await self.log_processing_result(
                user_id, document_id, extraction_result, validation_result
            )
            
            return {
                "success": True,
                "auto_approved": validation_result["is_valid"] and extraction_result["confidence"] > 0.85,
                "confidence_score": extraction_result["confidence"]
            }
            
        except Exception as e:
            await self.handle_processing_error(webhook_data, str(e))
            raise
    
    async def extract_document_data(self, document_url: str, document_type: str) -> Dict[str, Any]:
        """Extract structured data from KYC document"""
        try:
            # Use Composio to call document processing service
            result = await self.composio.execute_action(
                action=Action.CUSTOM_API_POST,
                params={
                    "url": "https://api.documentai.com/extract",  # Example OCR service
                    "headers": {"Authorization": "Bearer ${DOCUMENT_AI_API_KEY}"},
                    "json": {
                        "document_url": document_url,
                        "document_type": document_type,
                        "extract_fields": [
                            "license_number", "full_name", "date_of_birth", 
                            "expiry_date", "address", "blood_group"
                        ]
                    }
                }
            )
            
            return {
                "data": result.get("extracted_data", {}),
                "confidence": result.get("confidence_score", 0.0)
            }
            
        except Exception as e:
            # Fallback to manual processing
            return {
                "data": {},
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def validate_document_data(self, extraction_result: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """Validate extracted document data for compliance"""
        data = extraction_result.get("data", {})
        errors = []
        
        if document_type == "license":
            if not data.get("license_number"):
                errors.append("License number not found")
            if not data.get("expiry_date"):
                errors.append("Expiry date not found")
            if data.get("expiry_date"):
                try:
                    expiry = datetime.fromisoformat(data["expiry_date"])
                    if expiry < datetime.now():
                        errors.append("License has expired")
                except:
                    errors.append("Invalid expiry date format")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    async def auto_approve_document(self, user_id: str, document_id: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-approve KYC document"""
        result = await self.composio.execute_action(
            action=Action.CUSTOM_API_POST,
            params={
                "url": "${BACKEND_API_URL}/users/callbacks/kyc",
                "headers": {"Authorization": "Bearer ${BACKEND_API_TOKEN}"},
                "json": {
                    "user_id": user_id,
                    "document_id": document_id,
                    "status": "approved",
                    "extracted_data": extracted_data
                }
            }
        )
        return result
    
    async def flag_for_manual_review(self, user_id: str, document_id: str, document_type: str, errors: list, confidence: float):
        """Flag document for manual review via Slack"""
        message = f"""🔍 **KYC Document Requires Manual Review**

**User ID**: {user_id}
**Document Type**: {document_type}
**Confidence Score**: {confidence:.2f}

**Validation Issues**:
{chr(10).join(f'• {error}' for error in errors)}

**Actions Required**:
• Review document in admin panel
• Approve or reject with reason
• Update user KYC status

[Review Document](${BACKEND_API_URL}/admin/kyc/{document_id})"""

        await self.composio.execute_action(
            action=Action.SLACK_SEND_MESSAGE,
            params={
                "channel": "#kyc-review",
                "text": message
            }
        )
    
    async def notify_auto_approval(self, user_id: str, document_type: str):
        """Notify user of auto-approval"""
        # Send push notification via backend
        await self.composio.execute_action(
            action=Action.CUSTOM_API_POST,
            params={
                "url": "${BACKEND_API_URL}/notifications/send",
                "headers": {"Authorization": "Bearer ${BACKEND_API_TOKEN}"},
                "json": {
                    "user_id": user_id,
                    "type": "kyc_approved",
                    "title": "KYC Document Approved",
                    "message": f"Your {document_type} has been approved automatically. You can now access all platform features."
                }
            }
        )
    
    async def log_processing_result(self, user_id: str, document_id: str, extraction_result: Dict[str, Any], validation_result: Dict[str, Any]):
        """Log processing results to Notion and audit system"""
        # Log to Notion run log
        await self.composio.execute_action(
            action=Action.NOTION_CREATE_PAGE,
            params={
                "database_id": "${NOTION_RUN_LOG_DB_ID}",
                "properties": {
                    "Title": {"title": [{"text": {"content": f"KYC Processing - {user_id}"}}]},
                    "Status": {"select": {"name": "Auto-Approved" if validation_result["is_valid"] else "Manual Review"}},
                    "Document Type": {"select": {"name": document_type}},
                    "Confidence": {"number": extraction_result.get("confidence", 0)},
                    "Processing Time": {"date": {"start": datetime.now().isoformat()}},
                    "User ID": {"rich_text": [{"text": {"content": user_id}}]}
                }
            }
        )
        
        # Log to backend audit system
        await self.composio.execute_action(
            action=Action.CUSTOM_API_POST,
            params={
                "url": "${BACKEND_API_URL}/audit",
                "headers": {"Authorization": "Bearer ${BACKEND_API_TOKEN}"},
                "json": {
                    "event_type": "kyc_processing_completed",
                    "entity_type": "kyc_document",
                    "entity_id": document_id,
                    "action": "automated_processing",
                    "details": {
                        "confidence_score": extraction_result.get("confidence", 0),
                        "auto_approved": validation_result["is_valid"],
                        "validation_errors": validation_result.get("errors", [])
                    }
                }
            }
        )
    
    async def handle_processing_error(self, webhook_data: Dict[str, Any], error_message: str):
        """Handle processing errors"""
        # Alert operations team
        await self.composio.execute_action(
            action=Action.SLACK_SEND_MESSAGE,
            params={
                "channel": "#ev-platform-alerts",
                "text": f"""❌ **KYC Processing Failed**

**User ID**: {webhook_data.get('user_id')}
**Document ID**: {webhook_data.get('document_id')}
**Error**: {error_message}

Manual intervention required for KYC processing."""
            }
        )
        
        # Create Linear ticket for engineering
        await self.composio.execute_action(
            action=Action.LINEAR_CREATE_ISSUE,
            params={
                "title": f"KYC Processing Error - {webhook_data.get('user_id')}",
                "description": f"KYC processing failed for user {webhook_data.get('user_id')}\n\nError: {error_message}\n\nDocument ID: {webhook_data.get('document_id')}",
                "priority": 2,  # High priority
                "labels": ["bug", "kyc", "automation"]
            }
        )

# Rube workflow entry point
async def main(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for Rube workflow"""
    kyc_flow = KYCApprovalFlow()
    return await kyc_flow.process_kyc_document(webhook_data)

# Export for Rube
__all__ = ["main", "KYCApprovalFlow"]