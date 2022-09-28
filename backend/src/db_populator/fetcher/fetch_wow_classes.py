from asyncio import gather

from httpx import AsyncClient

from shared import Logger, re_try
from ..constants import MAX_RETRIES, TIMEOUT, ALL_CLASSES_API, CLASS_MEDIA_API


class FetchWowClassesHandler:

    logger: Logger
    access_token: str

    def __init__(self, logger: Logger, access_token: str) -> None:
        self.logger = logger
        self.access_token = access_token

    async def __call__(self):
        wow_classes: list[WowClassesDataclass] = await self.get_wow_classes()
        wow_classes = await self.get_wow_classes()

        _futures = []
        for wow_class in wow_classes:
            _futures.append(self.get_icon_for_wow_class(blizz_id=wow_class.blizz_id))
        _futures = await gather(*_futures)

        for index, wow_class in enumerate(wow_classes):
            wow_class.class_icon = _futures[index]

        return wow_classes

    def refactor_endpoint(self, tipo: str = "all-classes", *args, **kwargs):
        match tipo:
            case "all-classes":
                return ALL_CLASSES_API.replace("${accessToken}", self.access_token)
            case "class-icon":
                return CLASS_MEDIA_API.replace("${accessToken}", self.access_token).replace(
                    "${class_id}", str(kwargs.get("blizz_id"))
                )

    async def get_wow_classes(self):

        endpoint = self.refactor_endpoint()

        async with AsyncClient(timeout=TIMEOUT) as client:

            response = await client.get(endpoint)

            data = response.json()

            if response.status_code == 200:
                return self.format_returned_api_data(data=data)
            else:
                raise Exception(f"Houve um problema no status code ao solicitar os dados de todas as classes")

    def format_returned_api_data(self, data: dict):

        instances = []

        for key, val in data.items():
            if key == "classes":
                for wow_class in val:
                    instances.append(WowClassesDataclass(blizz_id=wow_class["id"], class_name=wow_class["name"]))

        return instances

    async def get_icon_for_wow_class(self, blizz_id: int):

        endpoint = self.refactor_endpoint(tipo="class-icon", blizz_id=blizz_id)

        async with AsyncClient(timeout=TIMEOUT) as client:

            response = await client.get(endpoint)

            data = response.json()

            if response.status_code == 200:
                return data["assets"][0]["value"]
            else:
                raise Exception(
                    f"Houve um problema no status code ao solicitar o ícone para a classe de blizz id {blizz_id}"
                )


@re_try(MAX_RETRIES)
async def fetch_wow_classes(logger: Logger, access_token: str):
    await logger.info("3 - Fetching wow classes data...")
    handler = FetchWowClassesHandler(logger=logger, access_token=access_token)
    return await handler()
