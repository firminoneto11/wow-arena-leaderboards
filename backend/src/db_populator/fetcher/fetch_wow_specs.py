from asyncio import gather

from httpx import AsyncClient, ConnectError, ConnectTimeout

from db_populator.constants import MAX_RETRIES, TIMEOUT, ALL_SPECS_API, SPEC_MEDIA_API
from shared import Logger, re_try
from ..schemas import WowSpecsSchema
from ..exceptions import CouldNotFetchError


class FetchWowSpecsHandler:

    logger: Logger
    access_token: str

    def __init__(self, logger: Logger, access_token: str) -> None:
        self.logger = logger
        self.access_token = access_token

    async def __call__(self) -> list[WowSpecsSchema]:

        wow_specs = {el.blizzard_id: el for el in await self.fetch_wow_specs()}

        icons: list[tuple[int, str]] = await gather(
            *[self.fetch_icon_for_wow_spec(blizzard_id=wow_specs[key].blizzard_id) for key in wow_specs.keys()]
        )

        for icon in icons:
            spec_id, icon_url = icon
            wow_specs[spec_id].icon_url = icon_url

        return list(map(lambda key: wow_specs[key], wow_specs.keys()))

    def refactor_endpoint(self, which: str, blizzard_id: int = 0) -> str:
        match which:
            case "specs":
                return ALL_SPECS_API.replace("{accessToken}", self.access_token)
            case "icon":
                return SPEC_MEDIA_API.replace("{accessToken}", self.access_token).replace("{specId}", str(blizzard_id))

    async def fetch_wow_specs(self) -> list[WowSpecsSchema]:

        endpoint = self.refactor_endpoint(which="specs")

        async with AsyncClient(timeout=TIMEOUT) as client:

            try:
                response = await client.get(endpoint)
            except (ConnectError, ConnectTimeout) as err:
                raise CouldNotFetchError(
                    f"A '{err.__class__.__name__}' occurred while fetching the wow specs's data."
                ) from err

            if response.status_code == 200:
                return self.format_returned_api_data(data=response.json())

            raise CouldNotFetchError("The server did not returned an OK response while fetching the wow specs's data")

    def format_returned_api_data(self, data: dict) -> list[WowSpecsSchema]:
        return [WowSpecsSchema(blizzard_id=spec["id"], name=spec["name"]) for spec in data["character_specializations"]]

    async def fetch_icon_for_wow_spec(self, blizzard_id: int) -> tuple[int, str]:

        endpoint = self.refactor_endpoint(which="icon", blizzard_id=blizzard_id)

        async with AsyncClient(timeout=TIMEOUT) as client:

            try:
                response = await client.get(endpoint)
            except (ConnectError, ConnectTimeout) as err:
                raise CouldNotFetchError(
                    f"A '{err.__class__.__name__}' occurred while fetching the icon for the wow spec of id {blizzard_id}."
                ) from err

            if response.status_code == 200:
                return blizzard_id, response.json()["assets"][0]["value"]

            raise CouldNotFetchError(
                f"The server did not returned an OK response while fetching the icon for the wow spec of id {blizzard_id}."
            )


@re_try(MAX_RETRIES)
async def fetch_wow_specs(logger: Logger, access_token: str) -> list[WowSpecsSchema]:
    await logger.info("4: Fetching wow specs's data...")
    handler = FetchWowSpecsHandler(logger=logger, access_token=access_token)
    response = await handler()
    await logger.info("Wow specs's data fetched successfully!")
    return response
