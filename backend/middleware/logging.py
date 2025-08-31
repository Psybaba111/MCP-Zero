"""
Logging middleware for EV Platform
Request/response logging with correlation IDs
"""

import logging
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

def setup_logging():
    """Setup application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with correlation IDs"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Log request
        start_time = time.time()
        logger = logging.getLogger("request")
        logger.info(
            f"Request started - {correlation_id} - {request.method} {request.url.path}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Request completed - {correlation_id} - {response.status_code} - {process_time:.3f}s"
        )
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response