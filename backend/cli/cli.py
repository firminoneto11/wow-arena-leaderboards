from .commands import runserver, init_db


def execute_from_command_line(command: str) -> None:
    """
    'runserver':
        Runs the development server\n

    'init':
        Initializes the ORM
    """

    valid_commands = ["runserver", "init"]

    if command not in valid_commands:
        raise RuntimeError(f"Invalid command chosen. Valid options are: {valid_commands!r}")

    match command:
        case "runserver":
            return runserver()
        case "init":
            return init_db()
