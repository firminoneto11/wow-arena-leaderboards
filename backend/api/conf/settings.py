from typing import Final as _Final
from pathlib import Path as _Path

from dynaconf import Dynaconf as _Dynaconf


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


TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        app: {
            "models": [f"{APPS_MODULE}.{app}.models"],
            "default_connection": "default",
        }
        for app in INSTALLED_APPS
    },
}


# The 'aerich.models' module has to be added only in the first one
first_key = list(TORTOISE_ORM["apps"])[0]
TORTOISE_ORM["apps"][first_key]["models"].append("aerich.models")
