import logging
import logging.config

from pydantic import BaseModel

logger = logging.getLogger("app")


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    version: int = 1

    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s | %(asctime)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": logging.DEBUG,
        },
    }
    loggers: dict = {
        "app": {
            "handlers": ["console"],
            "level": logging.INFO,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": logging.INFO,
        },
    }


log_config = LogConfig().dict()
logging.config.dictConfig(log_config)
