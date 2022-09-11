from asyncio import run, sleep
from logging import DEBUG, ERROR, INFO, FileHandler
from typing import NoReturn

from db_populator import UPDATE_EVERY, fetch_blizzard_api
from shared import AsyncLogger


async def main() -> NoReturn:
    """Entrypoint of this service."""

    # Creating the file handlers for the logger
    handlers = [
        {"handler": FileHandler(filename="populator_service.debug.log"), "level": DEBUG},
        {"handler": FileHandler(filename="populator_service.info.log"), "level": INFO},
        {"handler": FileHandler(filename="populator_service.error.log"), "level": ERROR},
    ]

    # Creating a logger with a custom name and the file handler
    logger = AsyncLogger(name="Populator Logs", file_handlers=handlers)

    # Loop that will be running forever to keep the database up to date with blizzard's data
    while True:
        await fetch_blizzard_api(logger=logger)
        await logger.log(f"Awaiting {UPDATE_EVERY} seconds before the next requests round")
        await sleep(UPDATE_EVERY)


if __name__ == "__main__":
    run(main(), debug=True)
