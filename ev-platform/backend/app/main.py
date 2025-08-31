from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import time
import uuid
from .core.config import settings
from .core.database import engine, Base
from .api.v1 import users, rides, vehicles, rentals, payments, rewards, compliance, audit

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="EV Platform API - Ride-hailing, Parcel Delivery, and P2P EV Rentals",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Include API routers
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(rides.router, prefix="/api/v1", tags=["rides"])
app.include_router(vehicles.router, prefix="/api/v1", tags=["vehicles"])
app.include_router(rentals.router, prefix="/api/v1", tags=["rentals"])
app.include_router(payments.router, prefix="/api/v1", tags=["payments"])
app.include_router(rewards.router, prefix="/api/v1", tags=["rewards"])
app.include_router(compliance.router, prefix="/api/v1", tags=["compliance"])
app.include_router(audit.router, prefix="/api/v1", tags=["audit"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to EV Platform API",
        "docs": "/docs",
        "health": "/health"
    }