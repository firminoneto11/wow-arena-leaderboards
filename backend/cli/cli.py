from .commands import runserver, MigrationsHandler


def execute_from_command_line(command: str) -> None:
    """
    'runserver': Runs the development server

    'initdb': Initializes the ORM - This command is very destructive since it completely resets the database and initializes a new ORM schema from scratch.

    'migrations': Generates the sql changes based on the models to be migrated.

    'migrate': Migrate the newly created sql changes against the database.
    """

    valid_commands = ["runserver", "initdb", "migrations", "migrate"]

    if command not in valid_commands:
        raise RuntimeError(f"Invalid command chosen. Valid options are: {valid_commands!r}")

    match command:
        case "runserver":
            return runserver()
        case "initdb" | "migrations" | "migrate":
            return MigrationsHandler.handle(choice=command)
