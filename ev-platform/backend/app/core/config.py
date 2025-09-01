from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/ev_platform"
    
    # Security
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Hyperswitch Payment Gateway
    HYPERSWITCH_PUBLIC_KEY: str = ""
    HYPERSWITCH_SECRET_KEY: str = ""
    HYPERSWITCH_WEBHOOK_SECRET: str = ""
    
    # External Services
    SLACK_BOT_TOKEN: str = ""
    SLACK_SIGNING_SECRET: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    NOTION_API_KEY: str = ""
    PAGERDUTY_API_KEY: str = ""
    
    # MCP-Zero
    MCP_ZERO_ENDPOINT: str = "http://localhost:8001"
    MCP_ZERO_ENABLED: bool = True
    
    # App Settings
    APP_NAME: str = "EV Platform"
    DEBUG: bool = True
    CORS_ORIGINS: list = ["*"]
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()