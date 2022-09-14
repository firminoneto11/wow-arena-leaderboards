from logging import LogRecord


class LogFilter:
    _level: int

    def __init__(self, level: int):
        self._level = level

    @property
    def level(self) -> int:
        return self._level

    def filter(self, record: LogRecord) -> bool:
        return self.level == record.levelno
