from dynaconf import Dynaconf


def _get_lazy_settings() -> Dynaconf:
    from api.config.settings import env_configs

    return env_configs


env_configs = _get_lazy_settings()
