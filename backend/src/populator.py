from asyncio import sleep

from db_populator import UPDATE_EVERY, fetch_blizzard_api, get_global_logger
from shared import run_main, CouldNotExecuteError


async def main():
    """Entrypoint of this service."""

    logger = get_global_logger()

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
