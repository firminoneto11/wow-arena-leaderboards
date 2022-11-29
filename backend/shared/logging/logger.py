from asyncio import to_thread as as_async
from functools import lru_cache
from os.path import exists
from os import makedirs
import logging as python_logging

from .utils import LogFilter, Handler


class Logger:
    """
    This Logger class is a nice wrapper around the regular Logger from the logging module. We can easily instantiate new loggers with it
    and also makes the log action asynchronous, because logging involves working with IO operations. There's also a sync api.

    The logger's level will always be DEBUG, but it is possible to set multiple file handlers to log different levels to different files.
    The stream handler's level will always be INFO
    """

    _logger: python_logging.Logger

    def __init__(
        self,
        *,
        name: str,
        fmt: python_logging.Formatter | None = None,
        handlers: list[Handler] = [],
    ) -> None:

        # Creating the log format to be used. Format options can be found at:
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        if fmt is None:  # pragma: no branch
            fmt = python_logging.Formatter(
                fmt="[%(levelname)s] [%(name)s] [%(asctime)s,%(msecs)d] -> %(message)s", datefmt="%d/%m/%Y %H:%M:%S"
            )

        # Creating or getting a logger object, and setting its level
        self._logger = python_logging.getLogger(name=name)
        self._logger.setLevel(level=python_logging.DEBUG)  # Always DEBUG

        # Setting the file handlers of the logger. A file handler can have different levels set, that way is possible to have a file
        # handler that only writes to the error log file in case of errors for example.
        for handler in handlers:
            if handler.log_only_one_level:  # pragma: no cover
                handler.file_handler.addFilter(filter=LogFilter(level=handler.level))

            handler.file_handler.setLevel(level=handler.level)
            handler.file_handler.setFormatter(fmt=fmt)
            self._logger.addHandler(handler.file_handler)

        # Adding a stream handler to spit the logs out in the console as well
        stream_handler = python_logging.StreamHandler()
        stream_handler.setLevel(level=python_logging.INFO)  # Always INFO to avoid spam in the stdout
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


@lru_cache(maxsize=10)
def get_logger(name: str) -> Logger:
    return _get_logger(name=name)
