from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING, FileHandler
from asyncio import sleep, to_thread as as_async
from os.path import exists, join
from typing import NoReturn
from os import mkdir

from db_populator import UPDATE_EVERY, fetch_blizzard_api
from shared import Logger, run_main


async def main() -> NoReturn:
    """Entrypoint of this service."""

    LOGS_PATH = "./logs"

    if not exists(LOGS_PATH):
        await as_async(mkdir, LOGS_PATH)

    # Creating the file handlers for the logger
    handlers = [
        {"handler": FileHandler(filename=join(LOGS_PATH, "debug.log")), "level": DEBUG, "log_every_level": False},
        {"handler": FileHandler(filename=join(LOGS_PATH, "info.log")), "level": INFO, "log_every_level": False},
        {"handler": FileHandler(filename=join(LOGS_PATH, "warning.log")), "level": WARNING, "log_every_level": False},
        {"handler": FileHandler(filename=join(LOGS_PATH, "error.log")), "level": ERROR, "log_every_level": False},
        {"handler": FileHandler(filename=join(LOGS_PATH, "critical.log")), "level": CRITICAL, "log_every_level": False},
        {"handler": FileHandler(filename=join(LOGS_PATH, "logs.log")), "level": DEBUG, "log_every_level": True},
    ]

    # Creating a logger with a custom name and the file handler
    logger = Logger(name="Populator Logs", file_handlers=handlers)

    # Loop that will be running forever to keep the database up to date with blizzard's data
    while True:
        await fetch_blizzard_api(logger=logger)
        await logger.info(f"Awaiting {UPDATE_EVERY} seconds before the next requests round")
        await sleep(UPDATE_EVERY)


if __name__ == "__main__":
    run_main(main)
