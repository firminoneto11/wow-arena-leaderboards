from typing import List
import logging

from .exceptions import InvalidLogLevelError
from .types import FileHandlersInterface
from .enums import LogLevels
from .filters import LogFilter
from ..utils import to_async


class AsyncLogger:
    """
    This Logger class is a nice wrapper around the regular Logger from the logging module. We can easily instantiate new loggers with it
    and also makes the log action asynchronous, because sometimes logging involves work with IO operations.

    The logger's level will always be DEBUG, but it is possible to set multiple file handlers to log different levels to different files.
    """

    _logger: logging.Logger

    def __init__(
        self,
        *,
        name: str,
        fmt: logging.Formatter | None = None,
        file_handlers: List[FileHandlersInterface] | None = None,
    ) -> None:

        # Creating the log format to be used. Format options can be found at:
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        if fmt is None:
            fmt = logging.Formatter("%(levelname)s - %(name)s - %(asctime)s - %(message)s")

        # Creating or getting a logger object, and setting its level to the chosen level
        self._logger = logging.getLogger(name=name)
        self._logger.setLevel(level=LogLevels.DEBUG.value)

        # Setting the file handlers of the logger. A file handler can have different levels set, that way is possible to have a file
        # handler that only writes to the log file in case of errors for example.
        if file_handlers is not None:
            for handler in file_handlers:
                _handler, _level = handler["handler"], handler["level"]

                _handler.setLevel(level=_level)
                _handler.setFormatter(fmt=fmt)
                _handler.addFilter(filter=LogFilter(level=_level))

                self._logger.addHandler(_handler)

        # Adding a stream handler to spit the logs out in the console as well
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(fmt=fmt)
        self._logger.addHandler(stream_handler)

    async def log(self, message: str, /, *, level: str = "INFO") -> None:
        """This method takes a message and logs it using the logger created."""

        chosen_level: LogLevels | None = getattr(LogLevels, level.upper(), None)

        if chosen_level is None:
            raise InvalidLogLevelError(f"The log level set is not valid. Valid options are: {LogLevels._member_names_}")

        chosen_level: int = chosen_level.value

        if chosen_level < self._logger.level:
            raise InvalidLogLevelError(
                f"The message won't be logged because the chosen log level is lower than the logger's level. Logger's level is"
                f"{self._logger.level} and the chosen level is {chosen_level}"
            )

        match level.upper():
            case "DEBUG":
                return await to_async(self._logger.debug, msg=message)
            case "INFO":
                return await to_async(self._logger.info, msg=message)
            case "WARNING":
                return await to_async(self._logger.warning, msg=message)
            case "ERROR":
                return await to_async(self._logger.error, msg=message)
            case "CRITICAL":
                return await to_async(self._logger.critical, msg=message)


class SyncLogger(AsyncLogger):
    """
    This Logger class is a nice wrapper around the regular Logger from the logging module. We can easily instantiate new loggers with it.
    The logger's level will always be DEBUG, but it is possible to set multiple file handlers to log different levels to different files.
    """

    def log(self, message: str, /, *, level: str = "INFO") -> None:
        """This method takes a message and logs it using the logger created."""

        _level = level.upper()

        chosen_level: LogLevels | None = getattr(LogLevels, _level, None)

        if chosen_level is None:
            raise InvalidLogLevelError(f"The log level set is not valid. Valid options are: {LogLevels._member_names_}")

        chosen_level: int = chosen_level.value

        if chosen_level < self._logger.level:
            raise InvalidLogLevelError(
                f"The message won't be logged because the chosen log level is lower than the logger's level. Logger's level is"
                f"{self._logger.level} and the chosen level is {chosen_level}"
            )

        match _level:
            case "DEBUG":
                return self._logger.debug(msg=message)
            case "INFO":
                return self._logger.info(msg=message)
            case "WARNING":
                return self._logger.warning(msg=message)
            case "ERROR":
                return self._logger.error(msg=message)
            case "CRITICAL":
                return self._logger.critical(msg=message)
