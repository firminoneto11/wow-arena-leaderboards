from decouple import config as get_env_var
from httpx import AsyncClient, ConnectError, ConnectTimeout

from shared import Logger
from ..decorators import re_try
from ..constants import TIMEOUT, BLIZZARD_TOKENS_URL, MAX_RETRIES
from ..schemas import OAuthTokenData  # , OAuthTokenError
from ..exceptions import CouldNotFetchError


@re_try(MAX_RETRIES)
async def fetch_token(logger: Logger) -> OAuthTokenData:
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
        except (ConnectError, ConnectTimeout) as err:
            raise CouldNotFetchError(f"A '{err.__class__.__name__}' occurred while fetching the access token.") from err

        if response.status_code == 200:
            schema = OAuthTokenData(**response.json())
            await logger.info("Access token fetched successfully!")
            return schema

        # schema = OAuthTokenError(**response.json())
        # message = "The server did not returned an OK response while fetching the access token."
        # await logger.warning(message + " Details:")
        # await logger.warning(schema.error)
        # await logger.warning(schema.error_description)
        raise CouldNotFetchError("The server did not returned an OK response while fetching the access token.")
