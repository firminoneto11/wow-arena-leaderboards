from typing import TypedDict
from logging import FileHandler


class FileHandlersInterface(TypedDict):
    handler: FileHandler
    level: int
