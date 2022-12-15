from typing import Final as _Final


def _get_lazy_settings():
    from api.conf import settings

    return settings


settings: _Final = _get_lazy_settings()
