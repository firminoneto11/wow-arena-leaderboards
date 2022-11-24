from functools import lru_cache
from os.path import exists
from os import makedirs
import logging as python_logging

from .handlers import Handler
from .logger import Logger


def _get_logger(name: str) -> Logger:
    from api.config.settings import LOGS_DIR

    if not exists(LOGS_DIR):
        makedirs(LOGS_DIR)

    # Creating the file handlers for the logger
    handlers = [
        Handler(
            file_handler=python_logging.FileHandler(filename=LOGS_DIR / f"{name}.log"),
            level=python_logging.DEBUG,
        ),
    ]

    # Creating a logger with a custom name and the file handler and returning it
    return Logger(name=name, handlers=handlers)


@lru_cache(maxsize=5)
def get_logger(name: str) -> Logger:
    return _get_logger(name=name)
