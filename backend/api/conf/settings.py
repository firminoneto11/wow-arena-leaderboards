from typing import Final as _Final
from pathlib import Path as _Path

from dynaconf import Dynaconf as _Dynaconf


def _add_migrations_app(tortoise_conf: dict) -> dict:
    # The 'aerich.models' module needs to be added in the first app's model list
    first_key = list(tortoise_conf["apps"])[0]
    tortoise_conf["apps"][first_key]["models"].append("aerich.models")

    return tortoise_conf


# Base directory of the project
BASE_DIR: _Final = _Path(__file__).resolve().parent.parent.parent


# Directory where the apps can be found
# APPS_DIR: _Final = BASE_DIR / "api" / "apps"


# Apps module
APPS_MODULE = "api.apps"


# Apps installed
INSTALLED_APPS: _Final = ["core"]


# Directory where the logs can be stored
LOGS_DIR: _Final = BASE_DIR / ".logs"


# Prefix for environment variables
ENV_PREFIX: _Final = "ARENA_API"


# Secrets files
SETTINGS_FILES: _Final = ["env.toml"]


# Env object
ENV: _Final = _Dynaconf(envvar_prefix=ENV_PREFIX, settings_files=SETTINGS_FILES)


# DB connection string
DATABASE_URL: _Final[str] = ENV.database_url


TORTOISE_ORM = _add_migrations_app(
    tortoise_conf={
        "connections": {"default": DATABASE_URL},
        "apps": {
            app: {
                "models": [f"{APPS_MODULE}.{app}.models"],
                "default_connection": "default",
            }
            for app in INSTALLED_APPS
        },
    }
)
