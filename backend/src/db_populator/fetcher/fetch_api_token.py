from decouple import config as get_env_var
from httpx import AsyncClient

from db_populator.constants import TIMEOUT, BLIZZARD_TOKENS_URL, MAX_RETRIES
from shared import async_timer, AsyncLogger
from ..schemas import OAuthTokenResponse, OAuthTokenData
from ..utils import re_try


@re_try(MAX_RETRIES)
@async_timer(5)
async def fetch_token(logger: AsyncLogger) -> OAuthTokenResponse:
    """
    This function makes a request to blizzard's server to get an updated access token.
    """

    credential_string: str = get_env_var("ENCODED_CREDENTIALS")
    content_type = "application/x-www-form-urlencoded"
    body = "grant_type=client_credentials"

    headers = {"Authorization": f"Basic {credential_string}", "Content-Type": content_type}

    raise Exception

    async with AsyncClient(timeout=TIMEOUT, headers=headers) as client:

        schema = OAuthTokenResponse()

        await logger.log("1: Fetching access token...")

        try:
            response = await client.post(url=BLIZZARD_TOKENS_URL, data=body)
        except Exception as error:
            schema.error, schema.message = True, str(error)
            await logger.log("An error occurred while fetching access token", level="error")
        else:
            schema.status_code = response.status_code
            if schema.status_code == 200:
                schema.data = OAuthTokenData(**response.json())
                await logger.log("Access token fetched successfully!")
            else:
                schema.message = response.text
                await logger.log("The server didn't send an OK response", level="error")
        finally:
            return schema
