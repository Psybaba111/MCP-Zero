"""
Pydantic schemas for Audit Service
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class AuditLogCreate(BaseModel):
    event_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    action: str
    details: Optional[Dict[str, Any]] = None

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    correlation_id: Optional[str]
    event_type: str
    user_id: Optional[uuid.UUID]
    entity_type: Optional[str]
    entity_id: Optional[uuid.UUID]
    action: str
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True