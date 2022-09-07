from asyncio import sleep, run as run_async
from typing import Final, NoReturn
import logging

from db_populator.settings import UPDATE_EVERY
from utils import as_async


async def main() -> NoReturn:
    """Entrypoint of this service."""

    # Creating the log format to be used. Format options can be found at:
    # https://docs.python.org/3/library/logging.html#logrecord-attributes
    LOG_FORMAT: Final[str] = "%(levelname)s - %(asctime)s - %(name)s - %(message)s"

    # Logs file name
    LOG_FILENAME: Final[str] = "db_populator_service.log"

    # Setting the basic log level to INFO, meaning that will be logged anything that is info or higher
    logging.basicConfig(level=logging.INFO, filename=LOG_FILENAME, format=LOG_FORMAT)

    # Creating a logger
    logger = logging.getLogger(name="Populator Logs")

    # Loop that will be running forever to keep the database up to date
    while True:
        await as_async(lambda: logger.info("Awaiting %s seconds before the next requests round", UPDATE_EVERY))
        await sleep(UPDATE_EVERY)


if __name__ == "__main__":
    run_async(main(), debug=True)
