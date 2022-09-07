from asyncio import sleep, run as run_async
from typing import NoReturn, Final
from logging import FileHandler

from db_populator.constants import UPDATE_EVERY
from shared import AsyncLogger


async def main() -> NoReturn:
    """Entrypoint of this service."""

    # Logs' file name
    LOG_FILENAME: Final[str] = "db_populator_service.log"

    # Creating a FileHandler for the logger
    file_handler = FileHandler(filename=LOG_FILENAME)

    # Creating a logger with a custom name and the file handler
    logger = AsyncLogger(name="Populator Logs", file_handler=file_handler)

    # Loop that will be running forever to keep the database up to date with blizzard's data
    while True:
        # await fetch_blizzard_api(logger=logger)
        await logger.log(f"Awaiting {UPDATE_EVERY} seconds before the next requests round")
        await sleep(UPDATE_EVERY)


if __name__ == "__main__":
    run_async(main(), debug=True)
