from typing import TypedDict, Literal
from logging import FileHandler


class FileHandlersInterface(TypedDict):
    handler: FileHandler
    level: int
    log_every_level: bool
