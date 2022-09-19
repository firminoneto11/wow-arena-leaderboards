from decouple import config as get_env_var
from httpx import AsyncClient

from db_populator.constants import TIMEOUT, BLIZZARD_TOKENS_URL, MAX_RETRIES
from shared import async_timer, AsyncLogger, re_try
from ..schemas import OAuthTokenResponse, OAuthTokenData, OAuthTokenErrorResponse


@re_try(MAX_RETRIES)
@async_timer(5)
async def fetch_token(logger: AsyncLogger) -> OAuthTokenData | OAuthTokenErrorResponse:
    """
    This function makes a request to blizzard's server to get an updated access token.
    """

    credential_string: str = get_env_var("ENCODED_CREDENTIALS")
    content_type = "application/x-www-form-urlencoded"
    body = "grant_type=client_credentials"

    headers = {"Authorization": f"Basic {credential_string}", "Content-Type": content_type}

    async with AsyncClient(timeout=TIMEOUT, headers=headers) as client:

        await logger.info("1: Fetching access token...")

        try:
            response = await client.post(url=BLIZZARD_TOKENS_URL, data=body)
        except Exception as error:
            await logger.error("An error occurred while fetching access token:")
            await logger.error(error)
        else:
            if response.status_code == 200:
                await logger.info("Access token fetched successfully!")
                return OAuthTokenData(**response.json())
            else:
                schema = OAuthTokenErrorResponse(**response.json())
                await logger.warning("The server did not returned an OK response. Details:")
                await logger.warning(schema.error)
                await logger.warning(schema.error_description)
                return schema
