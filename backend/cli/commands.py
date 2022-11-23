from asyncio import sleep, create_task, to_thread as as_async

from uvicorn import run as run_asgi_app
from rich import print as r_print
from traitlets.config import Config
import IPython

# Application imports
from api.apps.brackets import models
from database import db_engine

from service import fetch_blizzard_api
from service.constants import UPDATE_EVERY
from service.utils import get_global_logger
from service.exceptions import CouldNotExecuteError

from .decorators import close_event_loop_after_execution
from .context_managers import DbConnection


@close_event_loop_after_execution
async def migrate() -> None:
    await db_engine.create_all()
    r_print("Migrations completed successfully!")


@close_event_loop_after_execution
async def create_new_session() -> None:
    async with DbConnection():

        try:
            session = await as_async(input, "Insert the session number or 'q' to exit: ")
        except EOFError:
            r_print("Invalid input!")
            return await create_new_session()

        if session.strip().lower() == "q":
            return

        try:
            await models.Sessions.objects.create(session=session)
        except Exception as err:
            r_print(f"An error occurred while creating the session '{session}':")
            r_print(err)
        else:
            r_print("New session created successfully!")


@close_event_loop_after_execution
async def service():
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


def shell() -> None:
    shell_configs = Config()
    shell_configs.InteractiveShellApp.exec_lines = [
        "from api.apps.brackets import models",
        "from database import db_engine",
        "if not db_engine.db.is_connected: await db_engine.db.connect()",
    ]

    IPython.start_ipython(config=shell_configs, argv=[])

    # TODO: Check how to execute the line of code bellow after the shell finishes it's execution.
    # "if db_engine.db.is_connected: await db_engine.db.disconnect()",


def runserver() -> None:
    run_asgi_app("asgi:app", log_level="info", reload=True)
