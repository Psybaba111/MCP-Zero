"""
Deposit Release Automation for Rube.app
Automated processing of vehicle returns and deposit releases
"""

from composio import Composio, Action
import asyncio
from datetime import datetime
from typing import Dict, Any, List

class DepositReleaseAutomation:
    def __init__(self):
        self.composio = Composio()
        
    async def process_vehicle_return(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process vehicle return and handle deposit release
        Triggered when a rental is marked as returned
        """
        try:
            rental_id = webhook_data.get("rental_id")
            
            # Step 1: Fetch complete rental details
            rental_details = await self.fetch_rental_details(rental_id)
            
            # Step 2: Analyze return photos for damage
            damage_analysis = await self.analyze_return_photos(rental_details)
            
            # Step 3: Calculate deductions
            deduction_calculation = await self.calculate_deductions(rental_details, damage_analysis)
            
            # Step 4: Process refund if applicable
            refund_result = None
            if deduction_calculation["refund_amount"] > 0:
                refund_result = await self.process_deposit_refund(
                    rental_details, deduction_calculation["refund_amount"]
                )
            
            # Step 5: Notify all parties
            await self.notify_deposit_release(rental_details, deduction_calculation, refund_result)
            
            # Step 6: Log results
            await self.log_deposit_processing(rental_details, deduction_calculation, refund_result)
            
            return {
                "success": True,
                "rental_id": rental_id,
                "refund_amount": deduction_calculation["refund_amount"],
                "deduction_amount": deduction_calculation["deduction_amount"],
                "refund_processed": refund_result is not None
            }
            
        except Exception as e:
            await self.handle_processing_error(webhook_data, str(e))
            raise
    
    async def fetch_rental_details(self, rental_id: str) -> Dict[str, Any]:
        """Fetch complete rental information"""
        result = await self.composio.execute_action(
            action=Action.CUSTOM_API_GET,
            params={
                "url": f"${{BACKEND_API_URL}}/rentals/{rental_id}",
                "headers": {"Authorization": "Bearer ${BACKEND_API_TOKEN}"}
            }
        )
        return result
    
    async def analyze_return_photos(self, rental_details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze return photos for damage assessment"""
        return_photos = rental_details.get("return_photos", [])
        
        if not return_photos:
            return {"damage_detected": False, "severity": "none", "description": "No photos provided"}
        
        try:
            # Use AI image analysis (example with OpenAI Vision or similar)
            analysis_result = await self.composio.execute_action(
                action=Action.CUSTOM_API_POST,
                params={
                    "url": "https://api.openai.com/v1/chat/completions",
                    "headers": {"Authorization": "Bearer ${OPENAI_API_KEY}"},
                    "json": {
                        "model": "gpt-4-vision-preview",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Analyze these vehicle return photos for any damage. Rate severity as: none, minor, moderate, severe. Provide description of any damage found."
                                    },
                                    *[{"type": "image_url", "image_url": {"url": photo}} for photo in return_photos[:4]]
                                ]
                            }
                        ],
                        "max_tokens": 300
                    }
                }
            )
            
            # Parse AI response
            ai_response = analysis_result["choices"][0]["message"]["content"]
            
            # Simple parsing (in production, use more sophisticated NLP)
            damage_detected = "damage" in ai_response.lower() or "scratch" in ai_response.lower()
            severity = "minor"  # Default
            
            if "severe" in ai_response.lower():
                severity = "severe"
            elif "moderate" in ai_response.lower():
                severity = "moderate"
            elif not damage_detected:
                severity = "none"
            
            return {
                "damage_detected": damage_detected,
                "severity": severity,
                "description": ai_response
            }
            
        except Exception as e:
            # Fallback to manual review
            return {
                "damage_detected": False,
                "severity": "unknown",
                "description": f"Auto-analysis failed: {e}. Manual review required."
            }
    
    async def calculate_deductions(self, rental_details: Dict[str, Any], damage_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate deductions from deposit"""
        base_deposit = rental_details["deposit_amount"]
        total_deductions = 0
        deduction_reasons = []
        
        # Damage deductions
        if damage_analysis["damage_detected"]:
            severity = damage_analysis["severity"]
            if severity == "minor":
                damage_deduction = min(base_deposit * 0.1, 500)  # 10% or ₹500, whichever is lower
            elif severity == "moderate":
                damage_deduction = min(base_deposit * 0.3, 1500)  # 30% or ₹1500
            elif severity == "severe":
                damage_deduction = base_deposit  # Full deposit
            else:
                damage_deduction = 0
            
            if damage_deduction > 0:
                total_deductions += damage_deduction
                deduction_reasons.append(f"Vehicle damage ({severity}): ₹{damage_deduction}")
        
        # Late return deductions
        end_time = datetime.fromisoformat(rental_details["end_time"])
        if datetime.now() > end_time:
            late_hours = (datetime.now() - end_time).total_seconds() / 3600
            late_fee = min(late_hours * rental_details["hourly_rate"] * 1.5, base_deposit * 0.2)  # 1.5x rate or 20% deposit
            
            if late_fee > 0:
                total_deductions += late_fee
                deduction_reasons.append(f"Late return ({late_hours:.1f} hours): ₹{late_fee:.2f}")
        
        refund_amount = max(0, base_deposit - total_deductions)
        
        return {
            "deduction_amount": total_deductions,
            "refund_amount": refund_amount,
            "deduction_reasons": deduction_reasons
        }
    
    async def process_deposit_refund(self, rental_details: Dict[str, Any], refund_amount: float) -> Dict[str, Any]:
        """Process deposit refund through Hyperswitch"""
        try:
            refund_result = await self.composio.execute_action(
                action=Action.CUSTOM_API_POST,
                params={
                    "url": "https://sandbox.hyperswitch.io/refunds",
                    "headers": {"Authorization": "Bearer ${HYPERSWITCH_API_KEY}"},
                    "json": {
                        "payment_id": rental_details["deposit_payment_intent_id"],
                        "amount": int(refund_amount * 100),  # Convert to paise
                        "reason": "rental_deposit_release",
                        "metadata": {
                            "rental_id": rental_details["id"],
                            "user_id": rental_details["renter_id"]
                        }
                    }
                }
            )
            
            return {
                "refund_id": refund_result.get("refund_id"),
                "status": refund_result.get("status"),
                "amount": refund_amount
            }
            
        except Exception as e:
            print(f"Refund processing failed: {e}")
            return {"error": str(e)}
    
    async def notify_deposit_release(self, rental_details: Dict[str, Any], deduction_calculation: Dict[str, Any], refund_result: Dict[str, Any]):
        """Notify all parties about deposit processing"""
        # Notify renter
        if deduction_calculation["refund_amount"] == rental_details["deposit_amount"]:
            user_message = f"✅ **Full Deposit Refunded**\n\nYour security deposit of ₹{rental_details['deposit_amount']} has been fully refunded!\n\nThank you for taking good care of the vehicle. 🚗⚡"
        else:
            user_message = f"💰 **Deposit Processed**\n\nOriginal Deposit: ₹{rental_details['deposit_amount']}\nRefund Amount: ₹{deduction_calculation['refund_amount']}\nDeductions: ₹{deduction_calculation['deduction_amount']}\n\nDeduction Details:\n" + "\n".join(deduction_calculation["deduction_reasons"])
        
        # Send push notification to user
        await self.composio.execute_action(
            action=Action.CUSTOM_API_POST,
            params={
                "url": "${BACKEND_API_URL}/notifications/send",
                "headers": {"Authorization": "Bearer ${BACKEND_API_TOKEN}"},
                "json": {
                    "user_id": rental_details["renter_id"],
                    "type": "push_notification",
                    "title": "Deposit Processed",
                    "message": user_message
                }
            }
        )
        
        # Notify finance team via Slack
        finance_message = f"""💰 **Deposit Processed** - Rental {rental_details['id'][:8]}

**User:** {rental_details.get('renter_name', 'N/A')}
**Vehicle:** {rental_details.get('vehicle_make')} {rental_details.get('vehicle_model')}

**Financial Summary:**
• Original Deposit: ₹{rental_details['deposit_amount']}
• Refund Amount: ₹{deduction_calculation['refund_amount']}
• Deductions: ₹{deduction_calculation['deduction_amount']}

{f"**Deduction Breakdown:**\n" + chr(10).join(f"• {reason}" for reason in deduction_calculation['deduction_reasons']) if deduction_calculation['deduction_reasons'] else "**No deductions applied** ✅"}

**Refund ID:** {refund_result.get('refund_id', 'N/A')}"""

        await self.composio.execute_action(
            action=Action.SLACK_SEND_MESSAGE,
            params={
                "channel": "#finance-ops",
                "text": finance_message
            }
        )
    
    async def log_deposit_processing(self, rental_details: Dict[str, Any], deduction_calculation: Dict[str, Any], refund_result: Dict[str, Any]):
        """Log comprehensive audit entry"""
        await self.composio.execute_action(
            action=Action.CUSTOM_API_POST,
            params={
                "url": "${BACKEND_API_URL}/audit",
                "headers": {"Authorization": "Bearer ${BACKEND_API_TOKEN}"},
                "json": {
                    "event_type": "deposit_released",
                    "entity_type": "rental",
                    "entity_id": rental_details["id"],
                    "action": "deposit_processed",
                    "details": {
                        "original_deposit": rental_details["deposit_amount"],
                        "refund_amount": deduction_calculation["refund_amount"],
                        "deduction_amount": deduction_calculation["deduction_amount"],
                        "deduction_reasons": deduction_calculation["deduction_reasons"],
                        "refund_id": refund_result.get("refund_id") if refund_result else None,
                        "processing_time": datetime.now().isoformat()
                    }
                }
            }
        )
    
    async def handle_processing_error(self, webhook_data: Dict[str, Any], error_message: str):
        """Handle processing errors"""
        await self.composio.execute_action(
            action=Action.SLACK_SEND_MESSAGE,
            params={
                "channel": "#ev-platform-alerts",
                "text": f"""🚨 **Deposit Release Failed**

**Rental ID:** {webhook_data.get('rental_id')}
**Error:** {error_message}

Manual deposit processing required."""
            }
        )

# Rube workflow entry point
async def main(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for deposit release workflow"""
    automation = DepositReleaseAutomation()
    return await automation.process_vehicle_return(webhook_data)

# Export for Rube
__all__ = ["main", "DepositReleaseAutomation"]