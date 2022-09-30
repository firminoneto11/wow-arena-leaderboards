from typing import TypedDict
from asyncio import gather

from httpx import AsyncClient, ConnectError, ConnectTimeout

from db_populator.constants import TIMEOUT, BRAZILIAN_REALMS, PVP_RATING_API, MAX_RETRIES
from shared import Logger, re_try
from ..schemas import PvpDataSchema
from ..exceptions import CouldNotFetchError


class PvpDataType(TypedDict):
    _2s: list[PvpDataSchema]
    _3s: list[PvpDataSchema]
    rbg: list[PvpDataSchema]


class FetchHandler:

    logger: Logger
    access_token: str

    def __init__(self, logger: Logger, access_token: str) -> None:
        self.logger = logger
        self.access_token = access_token

    async def __call__(self) -> PvpDataType:
        _2s, _3s, rbg = await gather(
            self.fetch_data(session=33, bracket="2v2"),
            self.fetch_data(session=33, bracket="3v3"),
            self.fetch_data(session=33, bracket="rbg"),
        )

        return {
            "2s": self.clean_data(raw_data=_2s),
            "3s": self.clean_data(raw_data=_3s),
            "rbg": self.clean_data(raw_data=rbg),
        }

    def refactor_endpoint(self, session: int, bracket: str) -> str:
        return (
            PVP_RATING_API.replace("{session}", str(session))
            .replace("{bracket}", bracket)
            .replace("{accessToken}", self.access_token)
        )

    async def fetch_data(self, session: int, bracket: str) -> list[dict]:

        endpoint = self.refactor_endpoint(session=session, bracket=bracket)

        async with AsyncClient(timeout=TIMEOUT) as client:

            try:
                response = await client.get(endpoint)
            except (ConnectError, ConnectTimeout) as err:
                raise CouldNotFetchError(f"A '{err.__class__.__name__}' occurred while fetching the pvp data.") from err

            if response.status_code == 200:
                return list(
                    filter(
                        lambda player: player["character"]["realm"]["slug"] in BRAZILIAN_REALMS,
                        response.json()["entries"],
                    )
                )

            # TODO: Check how the non 200 response is returned
            # message = "The server did not returned an OK response while fetching the pvp data."
            # await self.logger.warning(message)
            raise CouldNotFetchError("The server did not returned an OK response while fetching the pvp data.")

    def clean_data(self, raw_data: list[dict]) -> list[PvpDataSchema]:
        return list(
            map(
                lambda el: PvpDataSchema(
                    blizzard_id=el["character"]["id"],
                    name=el["character"]["name"],
                    global_rank=el["rank"],
                    cr=el["rating"],
                    played=el["season_match_statistics"]["played"],
                    wins=el["season_match_statistics"]["won"],
                    losses=el["season_match_statistics"]["lost"],
                    faction_name=el["faction"]["type"],
                    realm=el["character"]["realm"]["slug"],
                    class_id=None,
                    spec_id=None,
                    avatar_icon=None,
                ),
                raw_data,
            )
        )


@re_try(MAX_RETRIES)
async def fetch_pvp_data(logger: Logger, access_token: str) -> PvpDataType:
    await logger.info("2: Fetching wow pvp data...")
    handler = FetchHandler(logger=logger, access_token=access_token)
    response = await handler()
    await logger.info("Wow pvp data fetched successfully!")
    return response
