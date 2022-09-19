from asyncio import to_thread as as_async
import logging

from .types import FileHandlersInterface
from .enums import LogLevels
from .filters import LogFilter


# TODO: Provide a single logger, with sync and async apis to log data


class AsyncLogger:
    """
    This Logger class is a nice wrapper around the regular Logger from the logging module. We can easily instantiate new loggers with it
    and also makes the log action asynchronous, because sometimes logging involves work with IO operations.

    The logger's level will always be DEBUG, but it is possible to set multiple file handlers to log different levels to different files.
    The stream handler's level will always be INFO
    """

    _logger: logging.Logger

    def __init__(
        self,
        *,
        name: str,
        fmt: logging.Formatter | None = None,
        file_handlers: list[FileHandlersInterface] | None = None,
    ) -> None:

        # Creating the log format to be used. Format options can be found at:
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        if fmt is None:
            fmt = logging.Formatter(
                fmt="%(levelname)s - %(name)s - %(asctime)s,%(msecs)d - %(message)s", datefmt="%d/%m/%Y %H:%M:%S"
            )

        # Creating or getting a logger object, and setting its level
        self._logger = logging.getLogger(name=name)
        self._logger.setLevel(level=LogLevels.DEBUG.value)  # Always DEBUG

        # Setting the file handlers of the logger. A file handler can have different levels set, that way is possible to have a file
        # handler that only writes to the error log file in case of errors for example.
        if file_handlers is not None:
            for handler in file_handlers:
                _handler, _level = handler["handler"], handler["level"]

                _handler.setLevel(level=_level)
                _handler.setFormatter(fmt=fmt)
                _handler.addFilter(filter=LogFilter(level=_level))

                self._logger.addHandler(_handler)

        # Adding a stream handler to spit the logs out in the console as well
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level=LogLevels.INFO.value)  # Always INFO
        stream_handler.setFormatter(fmt=fmt)
        self._logger.addHandler(stream_handler)

    async def debug(self, *args, **kwargs) -> None:
        await as_async(self._logger.debug, *args, **kwargs)

    async def info(self, *args, **kwargs) -> None:
        await as_async(self._logger.info, *args, **kwargs)

    async def warning(self, *args, **kwargs) -> None:
        await as_async(self._logger.warning, *args, **kwargs)

    async def error(self, *args, **kwargs) -> None:
        await as_async(self._logger.error, *args, **kwargs)

    async def critical(self, *args, **kwargs) -> None:
        await as_async(self._logger.critical, *args, **kwargs)

    async def exception(self, *args, **kwargs) -> None:
        await as_async(self._logger.exception, *args, **kwargs)


class SyncLogger(AsyncLogger):
    """
    This Logger class is a nice wrapper around the regular Logger from the logging module. We can easily instantiate new loggers with it.
    The logger's level will always be DEBUG, but it is possible to set multiple file handlers to log different levels to different files.
    The stream handler's level will always be INFO
    """

    def debug(self, *args, **kwargs) -> None:
        self._logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs) -> None:
        self._logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs) -> None:
        self._logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs) -> None:
        self._logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs) -> None:
        self._logger.critical(*args, **kwargs)

    def exception(self, *args, **kwargs) -> None:
        self._logger.exception(*args, **kwargs)
