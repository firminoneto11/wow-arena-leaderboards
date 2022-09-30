from asyncio import gather

from httpx import AsyncClient, ConnectError, ConnectTimeout

from db_populator.constants import MAX_RETRIES, TIMEOUT, ALL_CLASSES_API, CLASS_MEDIA_API
from shared import Logger, re_try
from ..schemas import WowClassSchema
from ..exceptions import CouldNotFetchError


class FetchWowClassesHandler:

    logger: Logger
    access_token: str

    def __init__(self, logger: Logger, access_token: str) -> None:
        self.logger = logger
        self.access_token = access_token

    async def __call__(self) -> list[WowClassSchema]:

        wow_classes = await self.fetch_wow_classes()

        classes_map = {el.blizzard_id: el for el in wow_classes}

        icons: list[tuple[int, str]] = await gather(
            *[self.fetch_icon(blizzard_id=wow_class.blizzard_id) for wow_class in wow_classes]
        )

        for icon in icons:
            class_id, icon_url = icon
            classes_map[class_id].icon_url = icon_url

        return wow_classes

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
                    f"A '{err.__class__.__name__}' occurred while fetching the wow classes data."
                ) from err

            if response.status_code == 200:
                return self.format_api_data(data=response.json())

            # TODO: Check how the non 200 response is returned
            # message = "The server did not returned an OK response while fetching the wow classes data."
            # await self.logger.warning(message)
            raise CouldNotFetchError("The server did not returned an OK response while fetching the wow classes data.")

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
            # message = f"The server did not returned an OK response while fetching the icon for the wow class of id {blizzard_id}."
            # await self.logger.warning(message)
            raise CouldNotFetchError(
                f"The server did not returned an OK response while fetching the icon for the wow class of id {blizzard_id}."
            )


@re_try(MAX_RETRIES)
async def fetch_wow_classes(logger: Logger, access_token: str) -> list[WowClassSchema]:
    await logger.info("3: Fetching wow classes data...")
    handler = FetchWowClassesHandler(logger=logger, access_token=access_token)
    response = await handler()
    await logger.info("Wow classes data fetched successfully!")
    return response
