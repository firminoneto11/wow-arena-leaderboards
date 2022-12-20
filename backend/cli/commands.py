from asyncio import run
from os import system

from tortoise.connection import connections
from uvicorn import run as run_app
from aerich import Command

from conf import settings

# import IPython

# # Application imports
# # from api.apps.core import models
# # from database import db_engine

# from service import fetch_blizzard_api
# from service.constants import UPDATE_EVERY
# from service.utils import get_global_logger
# from service.exceptions import CouldNotExecuteError

# from .decorators import close_event_loop_after_execution
# from .context_managers import DbConnection


# # @close_event_loop_after_execution
# # async def migrate() -> None:
# #     await db_engine.create_all()
# #     print("Migrations completed successfully!")


# @close_event_loop_after_execution
# async def create_new_session() -> None:
#     async with DbConnection():

#         try:
#             session = await as_async(input, "Insert the session number or 'q' to exit: ")
#         except EOFError:
#             print("Invalid input!")
#             return await create_new_session()

#         if session.strip().lower() == "q":
#             return

#         try:
#             await models.Sessions.objects.create(session=session)
#         except Exception as err:
#             print(f"An error occurred while creating the session '{session}':")
#             print(err)
#         else:
#             print("New session created successfully!")


# @close_event_loop_after_execution
# async def service():
#     """Entrypoint of the data fetching service."""

#     logger = get_global_logger()

#     # Loop that will be running forever to keep the database up to date with blizzard's data
#     while True:
#         try:
#             await fetch_blizzard_api(logger=logger)
#         except (CouldNotExecuteError, AssertionError) as err:
#             create_task(
#                 logger.critical(
#                     f"The execution of the '{fetch_blizzard_api.__name__}' coroutine could not finish. Details:"
#                 )
#             )
#             create_task(logger.critical(err))

#         create_task(logger.info(f"Awaiting {UPDATE_EVERY} seconds before the next requests round."))
#         await sleep(UPDATE_EVERY)


# def shell() -> None:
#     shell_configs = Config()
#     shell_configs.InteractiveShellApp.exec_lines = [
#         "from api.apps.brackets import models",
#         "from database import db_engine",
#         "if not db_engine.db.is_connected: await db_engine.db.connect()",
#     ]

#     IPython.start_ipython(config=shell_configs, argv=[])

#     # TODO: Check how to execute the line of code bellow after the shell finishes it's execution.
#     # "if db_engine.db.is_connected: await db_engine.db.disconnect()",


def runserver() -> None:
    run_app("api.conf.app:app", log_level="info", reload=True)


def initmigrations() -> None:
    async def handler(location: str, app: str) -> None:
        command = Command(tortoise_config=settings.TORTOISE_ORM, location=location, app=app)
        await command.init_db(safe=True)
        await connections.close_all()

    migrations_folder = (settings.BASE_DIR / "migrations").as_posix()

    system(f"rm -rf {migrations_folder} *.db*")

    run(handler(location=migrations_folder, app=list(settings.TORTOISE_ORM["apps"])[0]))
