from .commands import runserver


def execute_from_command_line(command: str) -> None:
    """
    Here's the options for COMMAND:

    'runserver':
        Runs the development server\n
    """

    valid_commands = ["runserver"]

    if command not in valid_commands:
        raise RuntimeError(f"Invalid command chosen. Valid options are: {valid_commands!r}")

    match command:
        case "runserver":
            return runserver()
