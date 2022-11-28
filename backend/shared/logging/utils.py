from logging import LogRecord, FileHandler
from dataclasses import dataclass


class LogFilter:
    _level: int

    def __init__(self, level: int):
        self._level = level

    @property
    def level(self) -> int:
        return self._level

    def filter(self, record: LogRecord) -> bool:
        return self.level == record.levelno


@dataclass
class Handler:
    file_handler: FileHandler
    level: int
    log_only_one_level: bool = False
