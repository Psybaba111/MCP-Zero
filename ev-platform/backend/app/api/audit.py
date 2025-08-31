from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.db.database import get_db
from app.models.audit import AuditLog, AuditEventType, AuditSeverity
from app.models.user import User
from app.schemas.audit import (
    AuditLogCreate, AuditLogResponse, AuditLogSearch,
    ComplianceReport, ComplianceDigest, AuditMetrics, AuditExport
)
from app.services.audit_service import audit_service

router = APIRouter()


@router.post("/logs", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_log(
    audit_data: AuditLogCreate,
    db: Session = Depends(get_db)
):
    """Create a new audit log entry"""
    try:
        # Validate user exists if provided
        if audit_data.user_id:
            user = db.query(User).filter(User.id == audit_data.user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        # Create audit log entry
        new_audit_log = AuditLog(
            event_type=audit_data.event_type,
            event_id=audit_data.event_id,
            correlation_id=audit_data.correlation_id,
            user_id=audit_data.user_id,
            ip_address=audit_data.ip_address,
            user_agent=audit_data.user_agent,
            session_id=audit_data.session_id,
            ride_id=audit_data.ride_id,
            rental_id=audit_data.rental_id,
            vehicle_id=audit_data.vehicle_id,
            payment_id=audit_data.payment_id,
            reward_id=audit_data.reward_id,
            event_data=audit_data.event_data,
            previous_state=audit_data.previous_state,
            new_state=audit_data.new_state,
            severity=audit_data.severity,
            source=audit_data.source,
            tags=audit_data.tags
        )
        
        db.add(new_audit_log)
        db.commit()
        db.refresh(new_audit_log)
        
        return new_audit_log
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audit log: {str(e)}"
        )


@router.get("/logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db)
):
    """Get audit log details by ID"""
    audit_log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    return audit_log


@router.get("/logs", response_model=List[AuditLogResponse])
async def search_audit_logs(
    event_type: Optional[AuditEventType] = None,
    user_id: Optional[int] = None,
    ride_id: Optional[int] = None,
    rental_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    payment_id: Optional[int] = None,
    severity: Optional[AuditSeverity] = None,
    source: Optional[str] = None,
    correlation_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search audit logs with filters"""
    query = db.query(AuditLog)
    
    # Apply filters
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if ride_id:
        query = query.filter(AuditLog.ride_id == ride_id)
    if rental_id:
        query = query.filter(AuditLog.rental_id == rental_id)
    if vehicle_id:
        query = query.filter(AuditLog.vehicle_id == vehicle_id)
    if payment_id:
        query = query.filter(AuditLog.payment_id == payment_id)
    if severity:
        query = query.filter(AuditLog.severity == severity)
    if source:
        query = query.filter(AuditLog.source == source)
    if correlation_id:
        query = query.filter(AuditLog.correlation_id == correlation_id)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    audit_logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return audit_logs


@router.get("/compliance/user/{user_id}", response_model=ComplianceReport)
async def get_user_compliance_report(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get compliance report for a specific user"""
    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user's compliance information
    kyc_status = user.kyc_status.value if user.kyc_status else "not_submitted"
    license_status = "verified" if user.license_verified else "not_verified"
    license_expiry = user.license_expiry
    
    # Calculate compliance score
    compliance_score = 0.0
    pending_actions = []
    
    if user.kyc_status == "verified":
        compliance_score += 40.0
    elif user.kyc_status == "pending":
        compliance_score += 20.0
        pending_actions.append("Complete KYC verification")
    else:
        pending_actions.append("Submit KYC documents")
    
    if user.license_verified:
        compliance_score += 30.0
    else:
        pending_actions.append("Verify driving license")
    
    if user.is_active:
        compliance_score += 20.0
    else:
        pending_actions.append("Activate account")
    
    if user.address and user.emergency_contact:
        compliance_score += 10.0
    else:
        pending_actions.append("Complete profile information")
    
    # Check license expiry
    if license_expiry and license_expiry < datetime.utcnow():
        license_status = "expired"
        pending_actions.append("Renew driving license")
        compliance_score -= 20.0
    
    elif license_expiry and license_expiry < datetime.utcnow() + timedelta(days=30):
        pending_actions.append("License expiring soon - renew within 30 days")
    
    # Determine risk level
    if compliance_score >= 80:
        risk_level = "low"
    elif compliance_score >= 60:
        risk_level = "medium"
    else:
        risk_level = "high"
    
    # Get last audit timestamp
    last_audit = db.query(AuditLog).filter(
        AuditLog.user_id == user_id,
        AuditLog.event_type.in_([
            AuditEventType.KYC_REQUESTED,
            AuditEventType.KYC_VERIFIED,
            AuditEventType.KYC_REJECTED,
            AuditEventType.USER_UPDATED
        ])
    ).order_by(AuditLog.created_at.desc()).first()
    
    last_audit_time = last_audit.created_at if last_audit else user.created_at
    
    return ComplianceReport(
        user_id=user_id,
        kyc_status=kyc_status,
        license_status=license_status,
        license_expiry=license_expiry,
        compliance_score=max(0.0, compliance_score),
        risk_level=risk_level,
        pending_actions=pending_actions,
        last_audit=last_audit_time
    )


@router.get("/compliance/digest", response_model=ComplianceDigest)
async def get_compliance_digest(
    db: Session = Depends(get_db)
):
    """Get overall compliance digest for the platform"""
    # Get user statistics
    total_users = db.query(User).count()
    kyc_pending = db.query(User).filter(User.kyc_status == "pending").count()
    kyc_verified = db.query(User).filter(User.kyc_status == "verified").count()
    kyc_rejected = db.query(User).filter(User.kyc_status == "rejected").count()
    
    # Get license statistics
    licenses_expiring_soon = db.query(User).filter(
        User.license_expiry < datetime.utcnow() + timedelta(days=30),
        User.license_expiry > datetime.utcnow()
    ).count()
    
    licenses_expired = db.query(User).filter(
        User.license_expiry < datetime.utcnow()
    ).count()
    
    # Get recent compliance alerts
    compliance_alerts = db.query(AuditLog).filter(
        AuditLog.event_type.in_([
            AuditEventType.LICENSE_EXPIRY_WARNING,
            AuditEventType.KYC_REJECTED,
            AuditEventType.FRAUD_DETECTED
        ]),
        AuditLog.created_at >= datetime.utcnow() - timedelta(days=7)
    ).order_by(AuditLog.created_at.desc()).limit(10).all()
    
    return ComplianceDigest(
        total_users=total_users,
        kyc_pending=kyc_pending,
        kyc_verified=kyc_verified,
        kyc_rejected=kyc_rejected,
        licenses_expiring_soon=licenses_expiring_soon,
        licenses_expired=licenses_expired,
        compliance_alerts=compliance_alerts,
        generated_at=datetime.utcnow()
    )


@router.get("/metrics", response_model=AuditMetrics)
async def get_audit_metrics(
    time_period: str = "24h",  # "1h", "24h", "7d", "30d"
    db: Session = Depends(get_db)
):
    """Get audit metrics for the specified time period"""
    # Calculate time range
    now = datetime.utcnow()
    if time_period == "1h":
        start_date = now - timedelta(hours=1)
    elif time_period == "24h":
        start_date = now - timedelta(days=1)
    elif time_period == "7d":
        start_date = now - timedelta(days=7)
    elif time_period == "30d":
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=1)
    
    # Get total events in period
    total_events = db.query(AuditLog).filter(
        AuditLog.created_at >= start_date
    ).count()
    
    # Get events by type
    events_by_type = {}
    event_types = db.query(AuditLog.event_type).filter(
        AuditLog.created_at >= start_date
    ).distinct().all()
    
    for event_type, in event_types:
        count = db.query(AuditLog).filter(
            AuditLog.event_type == event_type,
            AuditLog.created_at >= start_date
        ).count()
        events_by_type[event_type.value] = count
    
    # Get events by severity
    events_by_severity = {}
    severities = db.query(AuditLog.severity).filter(
        AuditLog.created_at >= start_date
    ).distinct().all()
    
    for severity, in severities:
        count = db.query(AuditLog).filter(
            AuditLog.severity == severity,
            AuditLog.created_at >= start_date
        ).count()
        events_by_severity[severity.value] = count
    
    # Get events by source
    events_by_source = {}
    sources = db.query(AuditLog.source).filter(
        AuditLog.created_at >= start_date,
        AuditLog.source.isnot(None)
    ).distinct().all()
    
    for source, in sources:
        count = db.query(AuditLog).filter(
            AuditLog.source == source,
            AuditLog.created_at >= start_date
        ).count()
        events_by_source[source] = count
    
    # Get correlation tracking stats
    correlation_tracking = {}
    correlation_ids = db.query(AuditLog.correlation_id).filter(
        AuditLog.created_at >= start_date,
        AuditLog.correlation_id.isnot(None)
    ).distinct().all()
    
    for correlation_id, in correlation_ids:
        count = db.query(AuditLog).filter(
            AuditLog.correlation_id == correlation_id,
            AuditLog.created_at >= start_date
        ).count()
        correlation_tracking[correlation_id] = count
    
    # Get external integration stats
    external_integrations = {}
    slack_events = db.query(AuditLog).filter(
        AuditLog.slack_thread_ts.isnot(None),
        AuditLog.created_at >= start_date
    ).count()
    external_integrations["slack"] = slack_events
    
    notion_events = db.query(AuditLog).filter(
        AuditLog.notion_page_id.isnot(None),
        AuditLog.created_at >= start_date
    ).count()
    external_integrations["notion"] = notion_events
    
    pagerduty_events = db.query(AuditLog).filter(
        AuditLog.pagerduty_incident_id.isnot(None),
        AuditLog.created_at >= start_date
    ).count()
    external_integrations["pagerduty"] = pagerduty_events
    
    return AuditMetrics(
        total_events=total_events,
        events_by_type=events_by_type,
        events_by_severity=events_by_severity,
        events_by_source=events_by_source,
        correlation_tracking=correlation_tracking,
        external_integrations=external_integrations,
        time_period=time_period,
        generated_at=datetime.utcnow()
    )


@router.post("/export")
async def export_audit_logs(
    export_request: AuditExport,
    db: Session = Depends(get_db)
):
    """Export audit logs in specified format"""
    try:
        # Apply filters to get logs
        query = db.query(AuditLog)
        
        filters = export_request.filters
        if filters.event_type:
            query = query.filter(AuditLog.event_type == filters.event_type)
        if filters.user_id:
            query = query.filter(AuditLog.user_id == filters.user_id)
        if filters.ride_id:
            query = query.filter(AuditLog.ride_id == filters.ride_id)
        if filters.rental_id:
            query = query.filter(AuditLog.rental_id == filters.rental_id)
        if filters.vehicle_id:
            query = query.filter(AuditLog.vehicle_id == filters.vehicle_id)
        if filters.payment_id:
            query = query.filter(AuditLog.payment_id == filters.payment_id)
        if filters.severity:
            query = query.filter(AuditLog.severity == filters.severity)
        if filters.source:
            query = query.filter(AuditLog.source == filters.source)
        if filters.correlation_id:
            query = query.filter(AuditLog.correlation_id == filters.correlation_id)
        if filters.start_date:
            query = query.filter(AuditLog.created_at >= filters.start_date)
        if filters.end_date:
            query = query.filter(AuditLog.created_at <= filters.end_date)
        
        # Get logs
        logs = query.order_by(AuditLog.created_at.desc()).all()
        
        # Convert to export format
        if export_request.format == "json":
            export_data = []
            for log in logs:
                log_data = {
                    "id": log.id,
                    "event_type": log.event_type.value,
                    "event_id": log.event_id,
                    "correlation_id": log.correlation_id,
                    "user_id": log.user_id,
                    "severity": log.severity.value,
                    "source": log.source,
                    "created_at": log.created_at.isoformat(),
                    "event_data": log.event_data
                }
                
                if export_request.include_metadata:
                    log_data.update({
                        "ip_address": log.ip_address,
                        "user_agent": log.user_agent,
                        "session_id": log.session_id,
                        "tags": log.tags
                    })
                
                export_data.append(log_data)
            
            return {
                "format": "json",
                "count": len(export_data),
                "data": export_data,
                "exported_at": datetime.utcnow().isoformat()
            }
        
        elif export_request.format == "csv":
            # In real app, generate CSV file
            return {
                "format": "csv",
                "count": len(logs),
                "message": "CSV export not implemented in this version",
                "exported_at": datetime.utcnow().isoformat()
            }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported export format"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export audit logs: {str(e)}"
        )


@router.get("/correlation/{correlation_id}", response_model=List[AuditLogResponse])
async def get_correlation_events(
    correlation_id: str,
    db: Session = Depends(get_db)
):
    """Get all events related to a specific correlation ID"""
    events = db.query(AuditLog).filter(
        AuditLog.correlation_id == correlation_id
    ).order_by(AuditLog.created_at).all()
    
    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No events found for this correlation ID"
        )
    
    return events


@router.get("/health")
async def audit_health_check():
    """Health check for audit service"""
    return {
        "status": "healthy",
        "service": "audit_service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "event_logging",
            "compliance_tracking",
            "correlation_tracking",
            "export_capabilities"
        ]
    }