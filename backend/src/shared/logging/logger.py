from asyncio import to_thread as as_async
import logging

from .types import FileHandlersInterface
from .filters import LogFilter


class Logger:
    """
    This Logger class is a nice wrapper around the regular Logger from the logging module. We can easily instantiate new loggers with it
    and also makes the log action asynchronous, because sometimes logging involves work with IO operations. There's also a sync api.

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
        self._logger.setLevel(level=logging.DEBUG)  # Always DEBUG

        # Setting the file handlers of the logger. A file handler can have different levels set, that way is possible to have a file
        # handler that only writes to the error log file in case of errors for example.
        if file_handlers is not None:
            for handler in file_handlers:
                _handler, _level, log_every_level = handler["handler"], handler["level"], handler["log_every_level"]

                if not log_every_level:
                    _handler.addFilter(filter=LogFilter(level=_level))

                _handler.setLevel(level=_level)
                _handler.setFormatter(fmt=fmt)
                self._logger.addHandler(_handler)

        # Adding a stream handler to spit the logs out in the console as well
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level=logging.INFO)  # Always INFO
        stream_handler.setFormatter(fmt=fmt)
        self._logger.addHandler(stream_handler)

    # Async Logging

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

    # Sync Logging

    def sDebug(self, *args, **kwargs) -> None:
        self._logger.debug(*args, **kwargs)

    def sInfo(self, *args, **kwargs) -> None:
        self._logger.info(*args, **kwargs)

    def sWarning(self, *args, **kwargs) -> None:
        self._logger.warning(*args, **kwargs)

    def sError(self, *args, **kwargs) -> None:
        self._logger.error(*args, **kwargs)

    def sCritical(self, *args, **kwargs) -> None:
        self._logger.critical(*args, **kwargs)

    def sException(self, *args, **kwargs) -> None:
        self._logger.exception(*args, **kwargs)
