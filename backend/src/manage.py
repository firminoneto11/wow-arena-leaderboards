from asyncio import sleep, create_task, get_running_loop, to_thread as as_async

from rich import print as r_print
import typer as cli

# Application imports
from api.apps.brackets import models

from database import db_engine

from shared import run_coroutine, Event, EventLoop

from service import fetch_blizzard_api
from service.constants import UPDATE_EVERY
from service.utils import get_global_logger
from service.exceptions import CouldNotExecuteError


class DbContextManager:
    async def __aenter__(self, *args, **kwargs) -> None:
        if not db_engine.db.is_connected:
            await db_engine.db.connect()

    async def __aexit__(self, *args, **kwargs) -> None:
        if db_engine.db.is_connected:
            await db_engine.db.disconnect()


def finish() -> None:
    loop: EventLoop = get_running_loop()
    loop.register_event(item=Event(name="cli-shutdown"))


async def _migrate() -> None:
    await db_engine.create_all()
    r_print("Migrations completed successfully!")
    finish()


async def _create_new_session() -> None:
    async with DbContextManager():
        session = await as_async(input, "Insert the session number: ")
        try:
            await models.Sessions.objects.create(session=session)
        except Exception as err:
            r_print(f"An error occurred while creating the session '{session}':")
            r_print(err)
        else:
            r_print("New session created successfully!")
    finish()


async def _service():
    """Entrypoint of the data fetching service."""

    logger = get_global_logger()

    # Loop that will be running forever to keep the database up to date with blizzard's data
    while True:
        try:
            await fetch_blizzard_api(logger=logger)
        except (CouldNotExecuteError, AssertionError) as err:
            create_task(
                logger.critical(
                    f"The execution of the '{fetch_blizzard_api.__name__}' coroutine could not finish. Details:"
                )
            )
            create_task(logger.critical(err))

        create_task(logger.info(f"Awaiting {UPDATE_EVERY} seconds before the next requests round."))
        await sleep(UPDATE_EVERY)


async def _shell() -> None:
    async with DbContextManager():
        # TODO: Find out how to spin up a ipython shell here
        ...
    finish()


def execute_from_command_line(command: str) -> None:
    valid_commands = ["migrate", "service", "shell", "createnewsession"]
    match command:
        case "migrate":
            return run_coroutine(_migrate)
        case "service":
            return run_coroutine(_service)
        case "shell":
            return run_coroutine(_shell)
        case "createnewsession":
            return run_coroutine(_create_new_session)
        case _:
            r_print("A valid command was not provided. Valid options are:")
            r_print(valid_commands)
            return


if __name__ == "__main__":
    cli.run(execute_from_command_line)
