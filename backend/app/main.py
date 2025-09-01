from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from .core.config import settings
from .core.logging import setup_logging
from .core.middleware import correlation_id_middleware
from .routers import health as health_router
from .routers import audit as audit_router
from .routers import users as users_router


def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name, default_response_class=ORJSONResponse)
    app.middleware("http")(correlation_id_middleware)

    app.include_router(health_router.router)
    app.include_router(audit_router.router)
    app.include_router(users_router.router)
    return app


app = create_app()