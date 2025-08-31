from fastapi import Request, Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.audit import AuditLog, AuditEventType, AuditSeverity
from app.core.config import settings
import json
import time
from typing import Optional, Dict, Any


class AuditService:
    def __init__(self):
        self.service_name = "audit_service"

    async def log_request(
        self,
        request: Request,
        response: Optional[Response],
        process_time: float,
        success: bool,
        error: Optional[str] = None
    ):
        """Log HTTP request/response for audit purposes"""
        try:
            # Get correlation ID from request state
            correlation_id = getattr(request.state, "correlation_id", None)
            
            # Extract request details
            event_data = {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "query_params": dict(request.query_params),
                "path_params": dict(request.path_params),
                "process_time": process_time,
                "success": success
            }
            
            if response:
                event_data["response_status"] = response.status_code
                event_data["response_headers"] = dict(response.headers)
            
            if error:
                event_data["error"] = error
            
            # Create audit log entry
            audit_log = AuditLog(
                event_type=AuditEventType.ERROR_OCCURRED if error else AuditEventType.AUTOMATION_TRIGGERED,
                correlation_id=correlation_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                event_data=event_data,
                severity=AuditSeverity.ERROR if error else AuditSeverity.INFO,
                source=f"{request.method} {request.url.path}",
                tags=["http_request", "api"]
            )
            
            # Save to database (async operation)
            await self._save_audit_log(audit_log)
            
        except Exception as e:
            # Fallback logging if audit fails
            print(f"Audit logging failed: {e}")

    async def log_error(
        self,
        request: Request,
        error: str,
        status_code: int
    ):
        """Log application errors for audit purposes"""
        try:
            correlation_id = getattr(request.state, "correlation_id", None)
            
            event_data = {
                "error": error,
                "status_code": status_code,
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers)
            }
            
            audit_log = AuditLog(
                event_type=AuditEventType.ERROR_OCCURRED,
                correlation_id=correlation_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                event_data=event_data,
                severity=AuditSeverity.ERROR,
                source=f"{request.method} {request.url.path}",
                tags=["error", "api"]
            )
            
            await self._save_audit_log(audit_log)
            
        except Exception as e:
            print(f"Error audit logging failed: {e}")

    async def log_event(
        self,
        event_type: AuditEventType,
        event_id: Optional[str] = None,
        user_id: Optional[int] = None,
        correlation_id: Optional[str] = None,
        event_data: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        source: Optional[str] = None,
        tags: Optional[list] = None,
        **kwargs
    ):
        """Log custom events for audit purposes"""
        try:
            audit_log = AuditLog(
                event_type=event_type,
                event_id=event_id,
                user_id=user_id,
                correlation_id=correlation_id,
                event_data=event_data,
                severity=severity,
                source=source or self.service_name,
                tags=tags or [],
                **kwargs
            )
            
            await self._save_audit_log(audit_log)
            
        except Exception as e:
            print(f"Custom event audit logging failed: {e}")

    async def log_kyc_event(
        self,
        user_id: int,
        event_type: AuditEventType,
        police_verification_id: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """Log KYC-related events"""
        event_data = {
            "police_verification_id": police_verification_id,
            "notes": notes,
            "timestamp": time.time()
        }
        
        await self.log_event(
            event_type=event_type,
            user_id=user_id,
            event_data=event_data,
            source="kyc_service",
            tags=["kyc", "compliance"]
        )

    async def log_payment_event(
        self,
        payment_id: int,
        event_type: AuditEventType,
        user_id: int,
        amount: int,
        currency: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log payment-related events"""
        event_data = {
            "payment_id": payment_id,
            "amount": amount,
            "currency": currency,
            "status": status,
            "metadata": metadata,
            "timestamp": time.time()
        }
        
        await self.log_event(
            event_type=event_type,
            event_id=str(payment_id),
            user_id=user_id,
            event_data=event_data,
            source="payment_service",
            tags=["payment", "financial"]
        )

    async def log_ride_event(
        self,
        ride_id: int,
        event_type: AuditEventType,
        user_id: int,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log ride-related events"""
        event_data = {
            "ride_id": ride_id,
            "status": status,
            "metadata": metadata,
            "timestamp": time.time()
        }
        
        await self.log_event(
            event_type=event_type,
            event_id=str(ride_id),
            user_id=user_id,
            event_data=event_data,
            source="ride_service",
            tags=["ride", "transport"]
        )

    async def log_rental_event(
        self,
        rental_id: int,
        event_type: AuditEventType,
        user_id: int,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log rental-related events"""
        event_data = {
            "rental_id": rental_id,
            "status": status,
            "metadata": metadata,
            "timestamp": time.time()
        }
        
        await self.log_event(
            event_type=event_type,
            event_id=str(rental_id),
            user_id=user_id,
            event_data=event_data,
            source="rental_service",
            tags=["rental", "p2p"]
        )

    async def log_compliance_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[int] = None,
        event_data: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.WARNING
    ):
        """Log compliance-related events"""
        await self.log_event(
            event_type=event_type,
            user_id=user_id,
            event_data=event_data,
            severity=severity,
            source="compliance_service",
            tags=["compliance", "regulatory"]
        )

    async def _save_audit_log(self, audit_log: AuditLog):
        """Save audit log to database"""
        try:
            # This would typically be an async database operation
            # For now, we'll simulate it
            print(f"Audit Log: {audit_log.event_type} - {audit_log.source}")
            
            # In a real implementation, you would:
            # db = get_db()
            # db.add(audit_log)
            # db.commit()
            
        except Exception as e:
            print(f"Failed to save audit log: {e}")

    async def get_audit_logs(
        self,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Retrieve audit logs with filters"""
        try:
            # This would typically query the database
            # For now, return empty list
            return []
            
        except Exception as e:
            print(f"Failed to retrieve audit logs: {e}")
            return []

    async def export_audit_logs(
        self,
        format: str = "json",
        filters: Optional[Dict[str, Any]] = None
    ):
        """Export audit logs in specified format"""
        try:
            # This would typically export logs from database
            # For now, return empty data
            return {
                "format": format,
                "data": [],
                "exported_at": time.time()
            }
            
        except Exception as e:
            print(f"Failed to export audit logs: {e}")
            return None


# Global audit service instance
audit_service = AuditService()