"""
Audit API routes
Unified audit logging and retrieval
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from database import get_db, User, UserRole
from middleware.auth import get_current_active_user, require_role
from services.audit_service import AuditService
from schemas.audit import AuditLogCreate, AuditLogResponse

router = APIRouter()

@router.post("/", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_log(
    audit_data: AuditLogCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new audit log entry"""
    audit_log = await AuditService.log_event(
        correlation_id=getattr(request.state, 'correlation_id', None),
        event_type=audit_data.event_type,
        user_id=current_user.id,
        entity_type=audit_data.entity_type,
        entity_id=audit_data.entity_id,
        action=audit_data.action,
        details=audit_data.details,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return audit_log

@router.get("/", response_model=List[AuditLogResponse])
async def get_audit_logs(
    user_id: Optional[uuid.UUID] = None,
    entity_type: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get audit logs (admin only)"""
    audit_logs = await AuditService.get_audit_logs(
        db=db,
        user_id=user_id,
        entity_type=entity_type,
        event_type=event_type,
        limit=limit,
        offset=offset
    )
    
    return audit_logs

@router.get("/my", response_model=List[AuditLogResponse])
async def get_my_audit_logs(
    entity_type: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's audit logs"""
    audit_logs = await AuditService.get_audit_logs(
        db=db,
        user_id=current_user.id,
        entity_type=entity_type,
        event_type=event_type,
        limit=limit,
        offset=offset
    )
    
    return audit_logs