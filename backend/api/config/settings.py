from typing import Final
from pathlib import Path

from dynaconf import Dynaconf


def _setup_environment(**kwargs) -> Dynaconf:
    return Dynaconf(**kwargs)


BASE_DIR: Final = Path(__file__).resolve().parent.parent.parent

LOGS_DIR: Final = BASE_DIR / ".logs"

ENV_PREFIX: Final = "ARENA_LEADERBOARDS_API"

SETTINGS_FILES: Final[list[str]] = [
    "env.toml",
]

env_configs = _setup_environment(envvar_prefix=ENV_PREFIX, settings_files=SETTINGS_FILES)
