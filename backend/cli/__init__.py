from rich import print as r_print

from ..shared import run_coroutine
from .commands import (
    migrate,
    service,
    shell,
    create_new_session,
    runserver,
)


def execute_from_command_line(command: str) -> None:
    """
    Here's the options for COMMAND:

    'migrate':
        Apply the model's DDL queries into the database\n
    'service':
        Starts the api fetching service\n
    'shell':
        Initializes a ipython shell\n
    'createnewsession':
        Creates a new session on table Sessions\n
    'runserver':
        Runs the development server\n
    """

    valid_commands = ["migrate", "service", "shell", "createnewsession", "runserver"]
    match command:
        case "migrate":
            return run_coroutine(migrate())
        case "service":
            return run_coroutine(service())
        case "shell":
            return shell()
        case "createnewsession":
            return run_coroutine(create_new_session())
        case "runserver":
            return runserver()
        case _:
            r_print("A valid command was not provided. Valid options are:")
            r_print(valid_commands)
            return
