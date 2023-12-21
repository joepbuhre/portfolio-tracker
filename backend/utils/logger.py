import logging
import os
import sys
from typing import ClassVar

class ExitOnCritical(logging.Handler):
    def emit(self, record):
        if record.levelno in (logging.CRITICAL,):
            exit()

# class PostMessage(logging.Handler):
#     def emit(self, record):



from pydantic import BaseModel

# class LogConfig(BaseModel):
#     """Logging configuration to be set for the server"""

#     LOGGER_NAME: str = "mycoolapp"
#     LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
#     LOG_LEVEL: str = "DEBUG"

#     version: ClassVar[int] = 1
#     disable_existing_loggers: bool = False
#     formatters: ClassVar[dict] = {
#         "default": {
#             "()": "uvicorn.logging.DefaultFormatter",
#             "fmt": LOG_FORMAT,
#             "datefmt": "%Y-%m-%d %H:%M:%S",
#         },
#     }
#     handlers: ClassVar[dict] = {
#         "default": {
#             "formatter": "default",
#             "class": "logging.StreamHandler",
#             "stream": "ext://sys.stderr",
#         },
#     }
#     loggers: ClassVar[dict] = {
#         LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
#     }

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",

        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "portfolio-logger": {"handlers": ["default"], "level": "DEBUG"},
    },
}

from logging.config import dictConfig
def get_logger(level: str = 'DEBUG'):

    log = logging.getLogger('portfolio-logger')
    dictConfig(log_config)

    # log.setLevel(level=os.getenv('LOG_LEVEL', level).upper())
    
    # define handler and formatter
    # handler = logging.StreamHandler()

    # add formatter to handler

    # add handler to logger
    log.addHandler(ExitOnCritical())  


    return log

log = get_logger()
log