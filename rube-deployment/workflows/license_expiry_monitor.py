"""
License Expiry Monitor for Rube.app
Daily monitoring and notification system for license renewals
"""

from composio import Composio, Action
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

class LicenseExpiryMonitor:
    def __init__(self):
        self.composio = Composio()
        
    async def run_daily_check(self) -> Dict[str, Any]:
        """
        Daily license expiry check workflow
        Runs at 00:00 IST via cron trigger
        """
        try:
            # Step 1: Fetch expiring licenses
            expiring_licenses = await self.fetch_expiring_licenses()
            
            # Step 2: Group by urgency
            urgency_groups = self.group_licenses_by_urgency(expiring_licenses)
            
            # Step 3: Send notifications based on urgency
            notification_results = await self.send_notifications(urgency_groups)
            
            # Step 4: Create calendar events for legal team
            calendar_results = await self.create_calendar_events(urgency_groups["urgent"])
            
            # Step 5: Send daily digest
            digest_result = await self.send_daily_digest(urgency_groups, notification_results)
            
            # Step 6: Log to Notion and audit
            await self.log_execution_results(urgency_groups, notification_results)
            
            return {
                "success": True,
                "licenses_processed": len(expiring_licenses),
                "urgent_cases": len(urgency_groups["urgent"]),
                "notifications_sent": notification_results["total_sent"],
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            await self.handle_execution_error(str(e))
            raise
    
    async def fetch_expiring_licenses(self) -> List[Dict[str, Any]]:
        """Fetch licenses expiring in the next 30 days"""
        result = await self.composio.execute_action(
            action=Action.CUSTOM_API_GET,
            params={
                "url": "${BACKEND_API_URL}/users/kyc/documents",
                "headers": {"Authorization": "Bearer ${BACKEND_API_TOKEN}"},
                "params": {
                    "document_type": "license",
                    "expiry_within_days": 30
                }
            }
        )
        
        return result.get("data", [])
    
    def group_licenses_by_urgency(self, licenses: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group licenses by urgency levels"""
        groups = {"urgent": [], "warning": [], "notice": []}
        now = datetime.now()
        
        for license_doc in licenses:
            try:
                expiry_date = datetime.fromisoformat(license_doc["expiry_date"])
                days_to_expiry = (expiry_date - now).days
                
                license_doc["days_to_expiry"] = days_to_expiry
                
                if days_to_expiry <= 7:
                    groups["urgent"].append(license_doc)
                elif days_to_expiry <= 14:
                    groups["warning"].append(license_doc)
                else:
                    groups["notice"].append(license_doc)
                    
            except Exception as e:
                print(f"Error processing license {license_doc.get('id')}: {e}")
                
        return groups
    
    async def send_notifications(self, urgency_groups: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Send notifications based on urgency"""
        total_sent = 0
        
        # Send urgent SMS notifications
        if urgency_groups["urgent"]:
            for license_doc in urgency_groups["urgent"]:
                try:
                    await self.composio.execute_action(
                        action=Action.TWILIO_SEND_SMS,
                        params={
                            "to": license_doc["user_phone"],
                            "body": f"""🚨 URGENT: Your driving license expires in {license_doc['days_to_expiry']} days!

License: {license_doc.get('license_number', 'N/A')}
Expiry: {license_doc['expiry_date'][:10]}

Please renew immediately to avoid service disruption.

- EV Platform Team"""
                        }
                    )
                    total_sent += 1
                except Exception as e:
                    print(f"Failed to send SMS to {license_doc['user_phone']}: {e}")
        
        # Send email reminders for all categories
        all_licenses = urgency_groups["urgent"] + urgency_groups["warning"] + urgency_groups["notice"]
        for license_doc in all_licenses:
            try:
                await self.send_email_reminder(license_doc)
                total_sent += 1
            except Exception as e:
                print(f"Failed to send email for license {license_doc.get('id')}: {e}")
        
        return {"total_sent": total_sent}
    
    async def send_email_reminder(self, license_doc: Dict[str, Any]):
        """Send email reminder to user"""
        urgency_emoji = "🚨" if license_doc["days_to_expiry"] <= 7 else "⚠️" if license_doc["days_to_expiry"] <= 14 else "ℹ️"
        
        email_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>{urgency_emoji} License Renewal Reminder</h2>
            
            <p>Dear {license_doc.get('user_name', 'User')},</p>
            
            <p>Your driving license is expiring soon:</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <strong>License Number:</strong> {license_doc.get('license_number', 'N/A')}<br>
                <strong>Expiry Date:</strong> {license_doc['expiry_date'][:10]}<br>
                <strong>Days Remaining:</strong> {license_doc['days_to_expiry']} days
            </div>
            
            <p>Please renew your license to continue using EV Platform services.</p>
            
            <p>Best regards,<br>EV Platform Team</p>
        </body>
        </html>
        """
        
        await self.composio.execute_action(
            action=Action.GMAIL_SEND_EMAIL,
            params={
                "to": license_doc["user_email"],
                "subject": f"License Renewal Required - {license_doc['days_to_expiry']} days remaining",
                "html": email_content
            }
        )
    
    async def create_calendar_events(self, urgent_licenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create calendar events for urgent follow-ups"""
        events_created = 0
        
        for license_doc in urgent_licenses:
            try:
                # Create follow-up event for legal team
                await self.composio.execute_action(
                    action=Action.GOOGLECALENDAR_CREATE_EVENT,
                    params={
                        "calendar_id": "legal@evplatform.com",
                        "summary": f"License Expiry Follow-up: {license_doc.get('user_name')}",
                        "description": f"""License expiry follow-up required:

User: {license_doc.get('user_name')}
License: {license_doc.get('license_number')}
Phone: {license_doc.get('user_phone')}
Expiry: {license_doc['expiry_date'][:10]}
Days Remaining: {license_doc['days_to_expiry']}

Action needed: Contact user for renewal status""",
                        "start": {
                            "dateTime": (datetime.now() + timedelta(days=1)).isoformat(),
                            "timeZone": "Asia/Kolkata"
                        },
                        "end": {
                            "dateTime": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
                            "timeZone": "Asia/Kolkata"
                        },
                        "attendees": [
                            {"email": "legal@evplatform.com"},
                            {"email": "ops@evplatform.com"}
                        ]
                    }
                )
                events_created += 1
            except Exception as e:
                print(f"Failed to create calendar event for {license_doc.get('user_name')}: {e}")
        
        return {"events_created": events_created}
    
    async def send_daily_digest(self, urgency_groups: Dict[str, List[Dict[str, Any]]], notification_results: Dict[str, Any]) -> Dict[str, Any]:
        """Send daily digest to operations team"""
        urgent_list = ""
        if urgency_groups["urgent"]:
            urgent_list = "\n".join([
                f"• {license['user_name']} - {license.get('license_number', 'N/A')} ({license['days_to_expiry']} days)"
                for license in urgency_groups["urgent"]
            ])
        
        digest_message = f"""📋 **Daily License Expiry Report** - {datetime.now().strftime('%Y-%m-%d')}

🚨 **Urgent (≤7 days):** {len(urgency_groups['urgent'])}
⚠️ **Warning (≤14 days):** {len(urgency_groups['warning'])}
ℹ️ **Notice (≤30 days):** {len(urgency_groups['notice'])}

**Total notifications sent:** {notification_results['total_sent']}

{f"**Urgent Cases:**\n{urgent_list}" if urgent_list else "No urgent cases today! 🎉"}

_Automated by EV Platform License Tracker_"""

        await self.composio.execute_action(
            action=Action.SLACK_SEND_MESSAGE,
            params={
                "channel": "#license-tracking",
                "text": digest_message
            }
        )
        
        return {"digest_sent": True}
    
    async def log_execution_results(self, urgency_groups: Dict[str, List[Dict[str, Any]]], notification_results: Dict[str, Any]):
        """Log execution results to Notion and audit system"""
        # Update Notion run log
        await self.composio.execute_action(
            action=Action.NOTION_CREATE_PAGE,
            params={
                "database_id": "${NOTION_RUN_LOG_DB_ID}",
                "properties": {
                    "Title": {"title": [{"text": {"content": f"License Reminder Run - {datetime.now().strftime('%Y-%m-%d')}"}}]},
                    "Type": {"select": {"name": "Scheduled"}},
                    "Status": {"select": {"name": "Completed"}},
                    "Licenses Processed": {"number": sum(len(group) for group in urgency_groups.values())},
                    "Notifications Sent": {"number": notification_results["total_sent"]},
                    "Urgent Cases": {"number": len(urgency_groups["urgent"])},
                    "Execution Time": {"date": {"start": datetime.now().isoformat()}}
                }
            }
        )
        
        # Log to audit system
        await self.composio.execute_action(
            action=Action.CUSTOM_API_POST,
            params={
                "url": "${BACKEND_API_URL}/audit",
                "headers": {"Authorization": "Bearer ${BACKEND_API_TOKEN}"},
                "json": {
                    "event_type": "license_reminder_completed",
                    "entity_type": "automation",
                    "action": "daily_digest",
                    "details": {
                        "total_licenses": sum(len(group) for group in urgency_groups.values()),
                        "urgent_count": len(urgency_groups["urgent"]),
                        "notifications_sent": notification_results["total_sent"],
                        "execution_time": datetime.now().isoformat()
                    }
                }
            }
        )
    
    async def handle_execution_error(self, error_message: str):
        """Handle workflow execution errors"""
        # Alert operations
        await self.composio.execute_action(
            action=Action.SLACK_SEND_MESSAGE,
            params={
                "channel": "#ev-platform-alerts",
                "text": f"""🚨 **License Reminder Workflow Failed**

**Error:** {error_message}
**Timestamp:** {datetime.now().isoformat()}

Manual intervention required for license tracking."""
            }
        )
        
        # Create PagerDuty incident for critical automation failure
        await self.composio.execute_action(
            action=Action.PAGERDUTY_CREATE_INCIDENT,
            params={
                "title": "License Reminder Automation Failed",
                "service_id": "${PAGERDUTY_SERVICE_ID}",
                "urgency": "high",
                "body": {
                    "type": "incident_body",
                    "details": f"License reminder automation failed with error: {error_message}"
                }
            }
        )

# Rube workflow entry point
async def main() -> Dict[str, Any]:
    """Main entry point for daily license check"""
    monitor = LicenseExpiryMonitor()
    return await monitor.run_daily_check()

# Export for Rube
__all__ = ["main", "LicenseExpiryMonitor"]