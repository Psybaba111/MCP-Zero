"""
Audit Service for EV Platform
Centralized audit logging with correlation tracking
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from database import SessionLocal, AuditLog

class AuditService:
    """Service for handling audit logging"""
    
    @staticmethod
    async def log_event(
        event_type: str,
        action: str,
        correlation_id: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log an audit event"""
        db = SessionLocal()
        try:
            audit_log = AuditLog(
                correlation_id=correlation_id or str(uuid.uuid4()),
                event_type=event_type,
                user_id=user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            
            return audit_log
        finally:
            db.close()
    
    @staticmethod
    async def log_error(
        event_type: str,
        details: Dict[str, Any],
        correlation_id: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> AuditLog:
        """Log an error event"""
        return await AuditService.log_event(
            event_type=event_type,
            action="error",
            correlation_id=correlation_id,
            user_id=user_id,
            entity_type="system",
            details=details
        )
    
    @staticmethod
    async def get_audit_logs(
        db: Session,
        user_id: Optional[uuid.UUID] = None,
        entity_type: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """Retrieve audit logs with filters"""
        query = db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        
        return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()