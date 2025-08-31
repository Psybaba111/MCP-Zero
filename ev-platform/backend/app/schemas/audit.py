from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.audit import AuditEventType, AuditSeverity


class AuditLogCreate(BaseModel):
    event_type: AuditEventType
    event_id: Optional[str] = None
    correlation_id: Optional[str] = None
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    ride_id: Optional[int] = None
    rental_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    payment_id: Optional[int] = None
    reward_id: Optional[int] = None
    event_data: Optional[Dict[str, Any]] = None
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    severity: AuditSeverity = AuditSeverity.INFO
    source: Optional[str] = None
    tags: Optional[List[str]] = None


class AuditLogResponse(BaseModel):
    id: int
    event_type: AuditEventType
    event_id: Optional[str]
    correlation_id: Optional[str]
    user_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    session_id: Optional[str]
    ride_id: Optional[int]
    rental_id: Optional[int]
    vehicle_id: Optional[int]
    payment_id: Optional[int]
    reward_id: Optional[int]
    event_data: Optional[Dict[str, Any]]
    previous_state: Optional[Dict[str, Any]]
    new_state: Optional[Dict[str, Any]]
    severity: AuditSeverity
    source: Optional[str]
    tags: Optional[List[str]]
    slack_thread_ts: Optional[str]
    notion_page_id: Optional[str]
    pagerduty_incident_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogSearch(BaseModel):
    event_type: Optional[AuditEventType] = None
    user_id: Optional[int] = None
    ride_id: Optional[int] = None
    rental_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    payment_id: Optional[int] = None
    severity: Optional[AuditSeverity] = None
    source: Optional[str] = None
    correlation_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


class ComplianceReport(BaseModel):
    user_id: int
    kyc_status: str
    license_status: str
    license_expiry: Optional[datetime]
    compliance_score: float
    risk_level: str  # "low", "medium", "high"
    pending_actions: List[str]
    last_audit: datetime


class ComplianceDigest(BaseModel):
    total_users: int
    kyc_pending: int
    kyc_verified: int
    kyc_rejected: int
    licenses_expiring_soon: int
    licenses_expired: int
    compliance_alerts: List[AuditLogResponse]
    generated_at: datetime


class AuditMetrics(BaseModel):
    total_events: int
    events_by_type: Dict[str, int]
    events_by_severity: Dict[str, int]
    events_by_source: Dict[str, int]
    correlation_tracking: Dict[str, int]
    external_integrations: Dict[str, int]
    time_period: str
    generated_at: datetime


class AuditExport(BaseModel):
    format: str = "json"  # "json", "csv", "xlsx"
    filters: AuditLogSearch
    include_metadata: bool = True
    compression: Optional[str] = None  # "gzip", "zip"