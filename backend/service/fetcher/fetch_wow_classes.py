from asyncio import gather

from httpx import AsyncClient, ConnectError, ConnectTimeout

from shared import Logger
from ..decorators import re_try
from ..constants import MAX_RETRIES, TIMEOUT, ALL_CLASSES_API, CLASS_MEDIA_API
from ..schemas import WowClassSchema
from ..exceptions import CouldNotFetchError


class FetchWowClassesHandler:

    logger: Logger
    access_token: str

    def __init__(self, logger: Logger, access_token: str) -> None:
        self.logger = logger
        self.access_token = access_token

    async def __call__(self) -> list[WowClassSchema]:

        wow_classes = {el.blizzard_id: el for el in await self.fetch_wow_classes()}

        icons: list[tuple[int, str]] = await gather(
            *[self.fetch_icon(blizzard_id=wow_classes[key].blizzard_id) for key in wow_classes.keys()]
        )

        for icon in icons:
            class_id, icon_url = icon
            wow_classes[class_id].icon_url = icon_url

        return list(map(lambda key: wow_classes[key], wow_classes.keys()))

    def refactor_endpoint(self, which: str, blizzard_id: int = 0) -> str:
        match which:
            case "classes":
                return ALL_CLASSES_API.replace("{accessToken}", self.access_token)
            case "icon":
                return CLASS_MEDIA_API.replace("{accessToken}", self.access_token).replace(
                    "{classId}", str(blizzard_id)
                )

    def format_api_data(self, data: dict) -> list[WowClassSchema]:
        return [WowClassSchema(blizzard_id=wow_class["id"], name=wow_class["name"]) for wow_class in data["classes"]]

    async def fetch_wow_classes(self) -> list[WowClassSchema]:

        endpoint = self.refactor_endpoint(which="classes")

        async with AsyncClient(timeout=TIMEOUT) as client:

            try:
                response = await client.get(endpoint)
            except (ConnectError, ConnectTimeout) as err:
                raise CouldNotFetchError(
                    f"A '{err.__class__.__name__}' occurred while fetching the wow classes's data."
                ) from err

            if response.status_code == 200:
                return self.format_api_data(data=response.json())

            # TODO: Check how the non 200 response is returned
            raise CouldNotFetchError(
                "The server did not returned an OK response while fetching the wow classes's data."
            )

    async def fetch_icon(self, blizzard_id: int) -> tuple[int, str]:

        endpoint = self.refactor_endpoint(which="icon", blizzard_id=blizzard_id)

        async with AsyncClient(timeout=TIMEOUT) as client:

            try:
                response = await client.get(endpoint)
            except (ConnectError, ConnectTimeout) as err:
                raise CouldNotFetchError(
                    f"A '{err.__class__.__name__}' occurred while fetching the icon for the wow class of id {blizzard_id}."
                ) from err

            if response.status_code == 200:
                return blizzard_id, response.json()["assets"][0]["value"]

            # TODO: Check how the non 200 response is returned
            raise CouldNotFetchError(
                f"The server did not returned an OK response while fetching the icon for the wow class of id {blizzard_id}."
            )


@re_try(MAX_RETRIES)
async def fetch_wow_classes(logger: Logger, access_token: str) -> list[WowClassSchema]:
    await logger.info("3: Fetching wow classes's data...")
    handler = FetchWowClassesHandler(logger=logger, access_token=access_token)
    response = await handler()
    await logger.info("Wow classes's data fetched successfully!")
    return response
