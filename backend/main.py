"""
EV Platform Backend - Main FastAPI Application
Serves ride-hailing, P2P EV rentals, and parcel delivery services
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from datetime import datetime
import logging

from database import init_db
from routers import users, vehicles, rides, parcels, rentals, payments, rewards, audit
from middleware.auth import get_current_user
from middleware.logging import setup_logging, LoggingMiddleware
from middleware.error_tracking import ErrorTrackingMiddleware, metrics

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting EV Platform Backend...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down EV Platform Backend...")

app = FastAPI(
    title="EV Platform API",
    description="Backend services for ride-hailing, P2P EV rentals, and parcel delivery",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(ErrorTrackingMiddleware)
app.add_middleware(LoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(vehicles.router, prefix="/api/v1/vehicles", tags=["vehicles"])
app.include_router(rides.router, prefix="/api/v1/rides", tags=["rides"])
app.include_router(parcels.router, prefix="/api/v1/parcels", tags=["parcels"])
app.include_router(rentals.router, prefix="/api/v1/rentals", tags=["rentals"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(rewards.router, prefix="/api/v1/rewards", tags=["rewards"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "EV Platform API",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "redis": "connected",  # TODO: Add Redis health check
            "hyperswitch": "connected"  # TODO: Add Hyperswitch health check
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    return {
        "metrics": metrics.get_metrics(),
        "timestamp": datetime.utcnow().isoformat()
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with audit logging"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Log to audit service
    try:
        from services.audit_service import AuditService
        await AuditService.log_error(
            event_type="system_error",
            details={
                "error": str(exc),
                "path": str(request.url),
                "method": request.method
            }
        )
    except Exception as audit_exc:
        logger.error(f"Failed to log audit: {audit_exc}")
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.utcnow().isoformat()}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )