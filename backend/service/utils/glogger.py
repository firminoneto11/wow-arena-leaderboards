from os.path import exists, join
from os import makedirs
import logging

from shared.logging.utils import Handler
from shared.logging import Logger
from ..constants import BASE_DIR


class GLogger:

    _logger: Logger = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self) -> None:
        if self._logger is None:
            self.setup()

    def setup(self) -> None:

        LOGS_DIR = BASE_DIR / "logs" / "service"
        if not exists(LOGS_DIR):
            makedirs(LOGS_DIR)

        # Creating the file handlers for the logger
        handlers = [
            Handler(file_handler=logging.FileHandler(filename=join(LOGS_DIR, "debug.log")), level=logging.DEBUG),
            Handler(file_handler=logging.FileHandler(filename=join(LOGS_DIR, "info.log")), level=logging.INFO),
            Handler(file_handler=logging.FileHandler(filename=join(LOGS_DIR, "warning.log")), level=logging.WARNING),
            Handler(file_handler=logging.FileHandler(filename=join(LOGS_DIR, "error.log")), level=logging.ERROR),
            Handler(file_handler=logging.FileHandler(filename=join(LOGS_DIR, "critical.log")), level=logging.CRITICAL),
            Handler(
                file_handler=logging.FileHandler(filename=join(LOGS_DIR, "logs.log")),
                log_only_one_level=False,
                level=logging.DEBUG,
            ),
        ]

        # Creating a logger with a custom name and the file handler
        self._logger = Logger(name="Service Logs", file_handlers=handlers)

    @property
    def logger(self) -> Logger:
        return self._logger

    @classmethod
    def get_instance(cls) -> Logger:
        cls().logger
