import logging.config

logger = logging.getLogger("app")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {name} {filename} {funcName}:{lineno:<10} [{levelname:.1s}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "null": {"class": "logging.NullHandler"},
    },
    "loggers": {
        "app": {"handlers": ["console"], "level": logging.DEBUG},
    },
    "root": {"handlers": ["null"]},
}

logging.config.dictConfig(LOGGING_CONFIG)

loggers = [logging.getLogger()]  # get the root logger
loggers = loggers + [logging.getLogger(name) for name in logging.root.manager.loggerDict]
