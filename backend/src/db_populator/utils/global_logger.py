from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING, FileHandler
from os.path import exists, join
from os import mkdir

from shared import Logger


class GlobalLogger:

    _logger: Logger | None = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self) -> None:
        if self._logger is None:
            self.setup()

    def setup(self) -> None:

        LOGS_PATH = "./logs"

        if not exists(LOGS_PATH):
            mkdir(LOGS_PATH)

        # Creating the file handlers for the logger
        handlers = [
            {"handler": FileHandler(filename=join(LOGS_PATH, "debug.log")), "level": DEBUG, "lock_log_level": True},
            {"handler": FileHandler(filename=join(LOGS_PATH, "info.log")), "level": INFO, "lock_log_level": True},
            {
                "handler": FileHandler(filename=join(LOGS_PATH, "warning.log")),
                "level": WARNING,
                "lock_log_level": True,
            },
            {"handler": FileHandler(filename=join(LOGS_PATH, "error.log")), "level": ERROR, "lock_log_level": True},
            {
                "handler": FileHandler(filename=join(LOGS_PATH, "critical.log")),
                "level": CRITICAL,
                "lock_log_level": True,
            },
            {"handler": FileHandler(filename=join(LOGS_PATH, "logs.log")), "level": DEBUG, "lock_log_level": False},
        ]

        # Creating a logger with a custom name and the file handler
        self._logger = Logger(name="Populator Logs", file_handlers=handlers)

    @property
    def logger(self) -> Logger:
        return self._logger


def get_global_logger() -> Logger:
    return GlobalLogger().logger
