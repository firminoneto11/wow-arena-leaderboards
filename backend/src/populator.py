from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING, FileHandler
from os.path import exists, join
from asyncio import run, sleep
from typing import NoReturn
from os import mkdir

from db_populator import UPDATE_EVERY, fetch_blizzard_api
from shared.utils import to_async, graceful_shutdown
from shared.logging import AsyncLogger


@graceful_shutdown
async def main() -> NoReturn:
    """Entrypoint of this service."""

    LOGS_PATH = "./logs"

    if not exists(LOGS_PATH):
        await to_async(mkdir, LOGS_PATH)

    # Creating the file handlers for the logger
    handlers = [
        {"handler": FileHandler(filename=join(LOGS_PATH, "debug.log")), "level": DEBUG},
        {"handler": FileHandler(filename=join(LOGS_PATH, "info.log")), "level": INFO},
        {"handler": FileHandler(filename=join(LOGS_PATH, "warning.log")), "level": WARNING},
        {"handler": FileHandler(filename=join(LOGS_PATH, "error.log")), "level": ERROR},
        {"handler": FileHandler(filename=join(LOGS_PATH, "critical.log")), "level": CRITICAL},
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
