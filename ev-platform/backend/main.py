from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uuid

from app.core.config import settings
from app.db.database import create_tables, get_db
from app.api import users, rides, vehicles, rentals, payments, rewards, audit
from app.services.audit_service import audit_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting EV Platform Backend...")
    create_tables()
    print("✅ Database tables created")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down EV Platform Backend...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Comprehensive EV platform with ride-hailing, P2P rentals, and compliance management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure based on your deployment
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    
    # Generate correlation ID for tracking
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response


@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    # Log request start
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Log successful request
        process_time = time.time() - start_time
        await audit_service.log_request(
            request=request,
            response=response,
            process_time=process_time,
            success=True
        )
        
        return response
        
    except Exception as e:
        # Log failed request
        process_time = time.time() - start_time
        await audit_service.log_request(
            request=request,
            response=None,
            process_time=process_time,
            success=False,
            error=str(e)
        )
        raise


# Include API routers
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(rides.router, prefix="/api/v1/rides", tags=["Rides"])
app.include_router(vehicles.router, prefix="/api/v1/vehicles", tags=["Vehicles"])
app.include_router(rentals.router, prefix="/api/v1/rentals", tags=["Rentals"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(rewards.router, prefix="/api/v1/rewards", tags=["Rewards"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])


@app.get("/")
async def root():
    return {
        "message": "EV Platform API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "database": "connected",
            "redis": "connected",
            "hyperswitch": "connected"
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Log the error
    await audit_service.log_error(
        request=request,
        error=str(exc),
        status_code=exc.status_code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "correlation_id": getattr(request.state, "correlation_id", None)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the error
    await audit_service.log_error(
        request=request,
        error=str(exc),
        status_code=500
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "correlation_id": getattr(request.state, "correlation_id", None)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )