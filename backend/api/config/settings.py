from typing import Final
from pathlib import Path

from dynaconf import Dynaconf


BASE_DIR: Final = Path(__file__).resolve().parent.parent.parent

LOGS_DIR: Final = BASE_DIR / ".logs"

ENV_PREFIX: Final = "ARENA_LEADERBOARDS_API"

SETTINGS_FILES: Final[list[str]] = [
    "env.toml",
]

env_configs = Dynaconf(envvar_prefix=ENV_PREFIX, settings_files=SETTINGS_FILES)
