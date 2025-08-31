"""
Ride Assignment Flow for Rube.app
Handles ride payment confirmations and driver assignments
"""

from composio import Composio, Action
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import random

class RideAssignmentFlow:
    def __init__(self):
        self.composio = Composio()
        
    async def process_ride_payment(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process ride payment confirmation and assign driver
        Triggered when ride payment is completed
        """
        try:
            entity_id = webhook_data.get("entity_id")
            
            # Step 1: Fetch ride details
            ride_details = await self.fetch_ride_details(entity_id)
            
            # Step 2: Find available driver
            driver_assignment = await self.find_available_driver(ride_details)
            
            # Step 3: Assign driver to ride
            if driver_assignment["driver_found"]:
                await self.assign_driver_to_ride(entity_id, driver_assignment)
                await self.notify_successful_assignment(ride_details, driver_assignment)
            else:
                await self.handle_no_driver_available(ride_details)
            
            # Step 4: Log assignment result
            await self.log_assignment_result(entity_id, driver_assignment)
            
            return {
                "success": True,
                "ride_id": entity_id,
                "driver_assigned": driver_assignment["driver_found"],
                "driver_id": driver_assignment.get("driver_id"),
                "eta_minutes": driver_assignment.get("eta_minutes")
            }
            
        except Exception as e:
            await self.handle_assignment_error(webhook_data, str(e))
            raise
    
    async def fetch_ride_details(self, ride_id: str) -> Dict[str, Any]:
        """Fetch complete ride information"""
        result = await self.composio.execute_action(
            action=Action.CUSTOM_API_GET,
            params={
                "url": f"${{BACKEND_API_URL}}/rides/{ride_id}",
                "headers": {"Authorization": "Bearer ${BACKEND_API_TOKEN}"}
            }
        )
        return result
    
    async def find_available_driver(self, ride_details: Dict[str, Any]) -> Dict[str, Any]:
        """Find available driver near pickup location"""
        try:
            # In production, this would call a sophisticated driver matching service
            # For MVP, we'll simulate driver availability
            
            # Mock driver pool based on vehicle type and location
            mock_drivers = [
                {
                    "driver_id": "driver_001",
                    "name": "Rajesh Kumar",
                    "phone": "+919876543210",
                    "vehicle_type": "scooter",
                    "rating": 4.8,
                    "distance_km": 2.5,
                    "eta_minutes": 8
                },
                {
                    "driver_id": "driver_002", 
                    "name": "Priya Sharma",
                    "phone": "+919876543211",
                    "vehicle_type": "bike",
                    "rating": 4.9,
                    "distance_km": 3.2,
                    "eta_minutes": 12
                },
                {
                    "driver_id": "driver_003",
                    "name": "Amit Singh",
                    "phone": "+919876543212", 
                    "vehicle_type": "car",
                    "rating": 4.7,
                    "distance_km": 1.8,
                    "eta_minutes": 6
                }
            ]
            
            # Filter by vehicle type and availability
            available_drivers = [
                d for d in mock_drivers 
                if d["vehicle_type"] == ride_details["vehicle_type"]
            ]
            
            if available_drivers:
                # Select closest driver
                best_driver = min(available_drivers, key=lambda d: d["distance_km"])
                
                return {
                    "driver_found": True,
                    "driver_id": best_driver["driver_id"],
                    "driver_name": best_driver["name"],
                    "driver_phone": best_driver["phone"],
                    "eta_minutes": best_driver["eta_minutes"],
                    "rating": best_driver["rating"]
                }
            else:
                return {"driver_found": False}
                
        except Exception as e:
            print(f"Driver matching failed: {e}")
            return {"driver_found": False, "error": str(e)}
    
    async def assign_driver_to_ride(self, ride_id: str, driver_assignment: Dict[str, Any]):
        """Update ride with assigned driver"""
        await self.composio.execute_action(
            action=Action.CUSTOM_API_PUT,
            params={
                "url": f"${{BACKEND_API_URL}}/rides/{ride_id}",
                "headers": {"Authorization": "Bearer ${BACKEND_API_TOKEN}"},
                "json": {
                    "driver_id": driver_assignment["driver_id"],
                    "status": "assigned"
                }
            }
        )
    
    async def notify_successful_assignment(self, ride_details: Dict[str, Any], driver_assignment: Dict[str, Any]):
        """Notify passenger and driver about assignment"""
        # Notify passenger
        passenger_message = f"""🚗 **Driver Assigned!**

**Driver:** {driver_assignment['driver_name']} ⭐ {driver_assignment['rating']}
**Vehicle:** {ride_details['vehicle_type'].title()}
**ETA:** {driver_assignment['eta_minutes']} minutes
**Contact:** {driver_assignment['driver_phone']}

Your driver is on the way to {ride_details['pickup_address']}"""

        await self.composio.execute_action(
            action=Action.CUSTOM_API_POST,
            params={
                "url": "${BACKEND_API_URL}/notifications/send",
                "headers": {"Authorization": "Bearer ${BACKEND_API_TOKEN}"},
                "json": {
                    "user_id": ride_details["passenger_id"],
                    "type": "push_notification",
                    "title": "Driver Assigned!",
                    "message": passenger_message
                }
            }
        )
        
        # Notify driver via SMS
        driver_message = f"""🎯 **New Ride Assignment**

Pickup: {ride_details['pickup_address']}
Drop: {ride_details['drop_address']}
Fare: ₹{ride_details['estimated_fare']}

Passenger: {ride_details.get('passenger_name', 'N/A')}
Phone: {ride_details.get('passenger_phone', 'N/A')}

Please head to pickup location."""

        await self.composio.execute_action(
            action=Action.TWILIO_SEND_SMS,
            params={
                "to": driver_assignment["driver_phone"],
                "body": driver_message
            }
        )
        
        # Notify operations team
        ops_message = f"""🚗 **Ride Assignment Completed**

**Ride ID:** {ride_details['id'][:8]}
**Driver:** {driver_assignment['driver_name']} ({driver_assignment['rating']}⭐)
**ETA:** {driver_assignment['eta_minutes']} minutes
**Route:** {ride_details['pickup_address']} → {ride_details['drop_address']}
**Fare:** ₹{ride_details['estimated_fare']}"""

        await self.composio.execute_action(
            action=Action.SLACK_SEND_MESSAGE,
            params={
                "channel": "#ride-ops",
                "text": ops_message
            }
        )
    
    async def handle_no_driver_available(self, ride_details: Dict[str, Any]):
        """Handle case when no driver is available"""
        # Alert operations team for manual assignment
        alert_message = f"""⚠️ **No Driver Available for Ride {ride_details['id'][:8]}**

**Location:** {ride_details['pickup_address']}
**Vehicle Type:** {ride_details['vehicle_type']}
**Fare:** ₹{ride_details['estimated_fare']}
**Passenger:** {ride_details.get('passenger_name', 'N/A')}

**Action Required:** Manual driver assignment needed

[Assign Driver](${BACKEND_API_URL}/admin/rides/{ride_details['id']}/assign)"""

        await self.composio.execute_action(
            action=Action.SLACK_SEND_MESSAGE,
            params={
                "channel": "#ride-ops",
                "text": alert_message
            }
        )
        
        # Create high-priority Linear ticket
        await self.composio.execute_action(
            action=Action.LINEAR_CREATE_ISSUE,
            params={
                "title": f"No Driver Available - Ride {ride_details['id'][:8]}",
                "description": f"Manual driver assignment required for ride {ride_details['id']}\n\nPickup: {ride_details['pickup_address']}\nVehicle Type: {ride_details['vehicle_type']}\n\nCustomer is waiting for assignment.",
                "priority": 1,  # Urgent
                "labels": ["operations", "driver-shortage", "urgent"]
            }
        )
    
    async def log_assignment_result(self, ride_id: str, driver_assignment: Dict[str, Any]):
        """Log assignment results to audit system"""
        await self.composio.execute_action(
            action=Action.CUSTOM_API_POST,
            params={
                "url": "${BACKEND_API_URL}/audit",
                "headers": {"Authorization": "Bearer ${BACKEND_API_TOKEN}"},
                "json": {
                    "event_type": "ride_assignment_processed",
                    "entity_type": "ride",
                    "entity_id": ride_id,
                    "action": "driver_assignment",
                    "details": {
                        "driver_assigned": driver_assignment["driver_found"],
                        "driver_id": driver_assignment.get("driver_id"),
                        "eta_minutes": driver_assignment.get("eta_minutes"),
                        "processing_time": datetime.now().isoformat()
                    }
                }
            }
        )
    
    async def handle_assignment_error(self, webhook_data: Dict[str, Any], error_message: str):
        """Handle assignment errors"""
        # Alert operations
        await self.composio.execute_action(
            action=Action.SLACK_SEND_MESSAGE,
            params={
                "channel": "#ev-platform-alerts",
                "text": f"""🚨 **Ride Assignment Failed**

**Ride ID:** {webhook_data.get('entity_id')}
**Error:** {error_message}

Critical: Customer payment processed but driver assignment failed.
Manual intervention required immediately."""
            }
        )
        
        # Create critical PagerDuty incident
        await self.composio.execute_action(
            action=Action.PAGERDUTY_CREATE_INCIDENT,
            params={
                "title": f"Critical: Ride Assignment Failed - {webhook_data.get('entity_id')}",
                "service_id": "${PAGERDUTY_SERVICE_ID}",
                "urgency": "high",
                "body": {
                    "type": "incident_body",
                    "details": f"Ride assignment automation failed. Customer paid but no driver assigned. Error: {error_message}"
                }
            }
        )

# Rube workflow entry point
async def main(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for ride assignment workflow"""
    flow = RideAssignmentFlow()
    return await flow.process_ride_payment(webhook_data)

# Export for Rube
__all__ = ["main", "RideAssignmentFlow"]