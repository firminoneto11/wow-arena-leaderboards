import logging

from .utils import as_async


class UnexpectedLevelError(Exception):
    ...


class AsyncLogger:
    """
    This Logger class is a nice wrapper around the regular Logger from the logging module. We can easily instantiate new loggers with it
    and also makes the log action asynchronous, because sometimes logging involves work with IO operations.
    """

    _logger: logging.Logger

    def __init__(
        self,
        *,
        name: str,
        level: int = logging.INFO,
        fmt: logging.Formatter | None = None,
        file_handler: logging.FileHandler | None = None,
    ) -> None:

        # Creating the log format to be used. Format options can be found at:
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        if fmt is None:
            fmt = logging.Formatter("%(levelname)s - %(name)s - %(asctime)s - %(message)s")

        # Creating or getting a logger object, and setting its level to the chosen level
        self._logger = logging.getLogger(name=name)
        self._logger.setLevel(level=level)

        # Setting the file handler of the logger. A file handler can have a different level set, that way is possible to have a file
        # handler that only writes to the log file in case of errors for example.
        if file_handler is not None:
            # file_handler.setLevel(level=logging.CRITICAL) -> Possible, but not needed right now
            file_handler.setFormatter(fmt=fmt)
            self._logger.addHandler(file_handler)

        # Adding a stream handler to spit the logs out in the console as well
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(fmt=fmt)
        self._logger.addHandler(stream_handler)

    async def log(self, message: str, /, *, level: str = "INFO") -> None:
        """This method takes a message and logs it using the logger created."""

        match level.upper():
            case "DEBUG":
                return await as_async(lambda: self._logger.debug(msg=message))
            case "INFO":
                return await as_async(lambda: self._logger.info(msg=message))
            case "WARNING":
                return await as_async(lambda: self._logger.warning(msg=message))
            case "ERROR":
                return await as_async(lambda: self._logger.error(msg=message))
            case "CRITICAL":
                return await as_async(lambda: self._logger.critical(msg=message))
            case _:
                raise UnexpectedLevelError("The level set to log the message is not valid")
