from .commands import runserver, initmigrations


def execute_from_command_line(command: str) -> None:
    """
    'runserver':
        Runs the development server\n

    'initmigrations':
        Initializes the ORM
    """

    valid_commands = ["runserver", "initmigrations"]

    if command not in valid_commands:
        raise RuntimeError(f"Invalid command chosen. Valid options are: {valid_commands!r}")

    match command:
        case "runserver":
            return runserver()
        case "initmigrations":
            return initmigrations()
