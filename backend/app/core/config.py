from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "EV Platform Backend"
    environment: str = "development"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ev_platform"

    jwt_secret: str = "dev-secret"
    hyperswitch_keys: str | None = None
    webhook_secret: str | None = None

    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()