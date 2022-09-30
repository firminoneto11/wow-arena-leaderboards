from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING, FileHandler
from asyncio import sleep, to_thread as as_async
from os.path import exists, join
from typing import NoReturn
from os import mkdir

from db_populator import UPDATE_EVERY, fetch_blizzard_api
from shared import Logger, run_main, CouldNotExecuteError


async def main() -> NoReturn:
    """Entrypoint of this service."""

    LOGS_PATH = "./logs"

    if not exists(LOGS_PATH):
        await as_async(mkdir, LOGS_PATH)

    # Creating the file handlers for the logger
    handlers = [
        {"handler": FileHandler(filename=join(LOGS_PATH, "debug.log")), "level": DEBUG, "lock_log_level": True},
        {"handler": FileHandler(filename=join(LOGS_PATH, "info.log")), "level": INFO, "lock_log_level": True},
        {"handler": FileHandler(filename=join(LOGS_PATH, "warning.log")), "level": WARNING, "lock_log_level": True},
        {"handler": FileHandler(filename=join(LOGS_PATH, "error.log")), "level": ERROR, "lock_log_level": True},
        {"handler": FileHandler(filename=join(LOGS_PATH, "critical.log")), "level": CRITICAL, "lock_log_level": True},
        {"handler": FileHandler(filename=join(LOGS_PATH, "logs.log")), "level": DEBUG, "lock_log_level": False},
    ]

    # Creating a logger with a custom name and the file handler
    logger = Logger(name="Populator Logs", file_handlers=handlers)

    # Loop that will be running forever to keep the database up to date with blizzard's data
    while True:
        try:
            await fetch_blizzard_api(logger=logger)
        except CouldNotExecuteError as err:
            await logger.critical(
                f"The execution of the '{fetch_blizzard_api.__name__}' coroutine could not finish. Details:"
            )
            await logger.critical(err)

        await logger.info(f"Awaiting {UPDATE_EVERY} seconds before the next requests round.")
        await sleep(UPDATE_EVERY)


if __name__ == "__main__":
    run_main(main)
