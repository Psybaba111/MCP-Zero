"""
Error tracking and observability middleware
Captures errors and metrics for monitoring
"""

import logging
import traceback
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import json

from services.audit_service import AuditService

logger = logging.getLogger(__name__)

class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for error tracking and observability"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            
            # Log 4xx and 5xx responses
            if response.status_code >= 400:
                await self._log_error_response(request, response)
            
            return response
        
        except Exception as exc:
            # Log unhandled exceptions
            await self._log_unhandled_exception(request, exc)
            raise
    
    async def _log_error_response(self, request: Request, response: Response):
        """Log error responses for monitoring"""
        try:
            await AuditService.log_event(
                correlation_id=getattr(request.state, 'correlation_id', None),
                event_type="http_error",
                entity_type="request",
                action="error_response",
                details={
                    "status_code": response.status_code,
                    "method": request.method,
                    "path": str(request.url.path),
                    "query_params": str(request.query_params),
                    "user_agent": request.headers.get("user-agent")
                },
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
        except Exception as e:
            logger.error(f"Failed to log error response: {e}")
    
    async def _log_unhandled_exception(self, request: Request, exc: Exception):
        """Log unhandled exceptions"""
        try:
            await AuditService.log_error(
                event_type="unhandled_exception",
                correlation_id=getattr(request.state, 'correlation_id', None),
                details={
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                    "traceback": traceback.format_exc(),
                    "method": request.method,
                    "path": str(request.url.path),
                    "query_params": str(request.query_params),
                    "user_agent": request.headers.get("user-agent")
                }
            )
        except Exception as e:
            logger.error(f"Failed to log unhandled exception: {e}")

class MetricsCollector:
    """Collects application metrics"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
    
    def record_request(self, duration: float, status_code: int):
        """Record request metrics"""
        self.request_count += 1
        self.response_times.append(duration)
        
        if status_code >= 500:
            self.error_count += 1
    
    def get_metrics(self) -> dict:
        """Get current metrics"""
        if not self.response_times:
            return {
                "request_count": self.request_count,
                "error_count": self.error_count,
                "error_rate": 0,
                "avg_response_time": 0,
                "p95_response_time": 0
            }
        
        sorted_times = sorted(self.response_times)
        p95_index = int(0.95 * len(sorted_times))
        
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": (self.error_count / self.request_count) * 100 if self.request_count > 0 else 0,
            "avg_response_time": sum(self.response_times) / len(self.response_times),
            "p95_response_time": sorted_times[p95_index] if sorted_times else 0
        }

# Global metrics collector
metrics = MetricsCollector()