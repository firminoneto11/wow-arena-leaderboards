from logging import FileHandler
from dataclasses import dataclass


@dataclass
class Handler:
    file_handler: FileHandler
    level: int
    log_only_one_level: bool = True
