from typing import Literal, Callable, Awaitable
from traceback import format_exc

from httpx import AsyncClient, Response

from ..exceptions import NetworkError, StatusCodeError
from .glogger import GLogger


_TIMEOUT = 30
_BASE_URL = ""


async def fetch(
    endpoint: str, failure_detail: str = "", method: Literal["GET", "POST"] = "GET", expected_status_code: int = 200,
    raise_for_status: bool = True
) -> Response:

    allowed_http_methods = ["GET", "POST"]
    logger = GLogger.get_instance()

    if method not in allowed_http_methods:
        raise ValueError(f"Http Method {method!r} is not valid. Valid choices are: {allowed_http_methods!r}")

    if raise_for_status and not failure_detail:
        raise ValueError(
            "When the 'raise_for_status' param is set to true, you should set a string value for the 'failure_detail' param."
        )

    async with AsyncClient(base_url=_BASE_URL, timeout=_TIMEOUT) as client:
        client_method: Callable[[str], Awaitable[Response]] = getattr(client, method.lower())
        try:
            response = await client_method(endpoint)
        except:
            message, traceback = "An error occurred while requesting the blizzard's api.", format_exc()
            await logger.error(f"{message} Details:\n{format_exc()}")
            raise NetworkError(detail=message, traceback=traceback)

    if (response.status_code == expected_status_code) or (not raise_for_status):
        return response

    raise StatusCodeError(detail=failure_detail, extra_data=response.json())
