import sys
from loguru import logger


def setup_logging(level: str = "INFO") -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        format=(
            "{time:YYYY-MM-DDTHH:mm:ss.SSS} | {level: <8} | {extra[cid]:-36} | "
            "{name}:{function}:{line} - {message}"
        ),
        backtrace=False,
        diagnose=False,
    )