import logging

from app.core.config import settings


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("excel-agent")
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)

    return logger


logger = setup_logger()
