from asyncio import gather

from httpx import AsyncClient, ConnectError

from shared import Logger, re_try
from ..schemas import WowClassSchema
from ..constants import MAX_RETRIES, TIMEOUT, ALL_CLASSES_API, CLASS_MEDIA_API


class FetchWowClassesHandler:

    logger: Logger
    access_token: str

    def __init__(self, logger: Logger, access_token: str) -> None:
        self.logger = logger
        self.access_token = access_token

    async def __call__(self) -> list[WowClassSchema] | None:
        wow_classes = await self.fetch_wow_classes()
        if wow_classes:
            icons: list[str] = await gather(
                *[self.fetch_icon(blizzard_id=wow_class.blizzard_id) for wow_class in wow_classes]
            )
            for (idx, wow_class) in enumerate(wow_classes):
                wow_class.icon_url = icons[idx]

            return wow_classes

    def refactor_endpoint(self, which: str, blizzard_id: int = 0) -> str:
        match which:
            case "classes":
                return ALL_CLASSES_API.replace("{accessToken}", self.access_token)
            case "icon":
                return CLASS_MEDIA_API.replace("{accessToken}", self.access_token).replace(
                    "{classId}", str(blizzard_id)
                )

    def format_api_data(self, data: dict) -> list[WowClassSchema] | None:
        wow_classes: list[dict] | None = data.get("classes")
        if wow_classes is None:
            return
        return [WowClassSchema(blizzard_id=wow_class["id"], name=wow_class["name"]) for wow_class in wow_classes]

    async def fetch_wow_classes(self) -> list[WowClassSchema] | None:
        endpoint = self.refactor_endpoint(which="classes")
        async with AsyncClient(timeout=TIMEOUT) as client:
            try:
                response = await client.get(endpoint)
            except ConnectError as err:
                await self.logger.error("A ConnectError occurred while fetching the wow classes data. Details:")
                await self.logger.error(err)
            else:
                if response.status_code == 200:
                    return self.format_api_data(data=response.json())

                # TODO: Check how the non 200 response is returned
                await self.logger.warning(
                    "The server did not returned an OK response while fetching the wow classes data."
                )

    async def fetch_icon(self, blizzard_id: int) -> str | None:
        endpoint = self.refactor_endpoint(which="icon", blizzard_id=blizzard_id)
        async with AsyncClient(timeout=TIMEOUT) as client:
            try:
                response = await client.get(endpoint)
            except ConnectError as err:
                await self.logger.error(
                    f"A ConnectError occurred while fetching the icon for the wow class of id {blizzard_id}. Details:"
                )
                await self.logger.error(err)
            else:
                if response.status_code == 200:
                    return response.json()["assets"][0]["value"]

                # TODO: Check how the non 200 response is returned
                await self.logger.warning(
                    f"The server did not returned an OK response while fetching the icon for the wow class of id {blizzard_id}."
                )


@re_try(MAX_RETRIES)
async def fetch_wow_classes(logger: Logger, access_token: str):
    await logger.info("3: Fetching wow classes data...")
    handler = FetchWowClassesHandler(logger=logger, access_token=access_token)
    return await handler()
