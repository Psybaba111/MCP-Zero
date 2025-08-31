import uuid
from typing import Callable

from fastapi import Request, Response
from loguru import logger


async def correlation_id_middleware(request: Request, call_next: Callable):
    correlation_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    with logger.contextualize(cid=correlation_id):
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = correlation_id
        return response