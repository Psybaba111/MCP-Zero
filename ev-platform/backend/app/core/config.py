from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/ev_platform"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Hyperswitch Payment
    HYPERSWITCH_PUBLISHABLE_KEY: str = ""
    HYPERSWITCH_SECRET_KEY: str = ""
    HYPERSWITCH_WEBHOOK_SECRET: str = ""
    
    # External Services
    SLACK_BOT_TOKEN: str = ""
    SLACK_SIGNING_SECRET: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    NOTION_TOKEN: str = ""
    NOTION_DATABASE_ID: str = ""
    
    # MCP-Zero
    MCP_ZERO_ENDPOINT: str = "http://localhost:8001"
    MCP_ZERO_ENABLED: bool = True
    
    # AI Services
    VLLM_ENDPOINT: str = "http://localhost:8002"
    OLLAMA_ENDPOINT: str = "http://localhost:11434"
    
    # App Settings
    APP_NAME: str = "EV Platform"
    DEBUG: bool = True
    CORS_ORIGINS: list = ["*"]
    
    # Compliance
    POLICE_KYC_CALLBACK_URL: str = ""
    HIGH_VALUE_REFUND_THRESHOLD: int = 5000  # ₹5000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()