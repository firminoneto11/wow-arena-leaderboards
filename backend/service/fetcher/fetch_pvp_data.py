from asyncio import gather

from httpx import AsyncClient, ConnectError, ConnectTimeout

from api.apps.core import BracketsEnum
from shared import Logger
from ..decorators import re_try
from ..constants import TIMEOUT, BRAZILIAN_REALMS, PVP_RATING_API, MAX_RETRIES
from ..schemas import PvpDataSchema
from ..exceptions import CouldNotFetchError


class FetchHandler:

    logger: Logger
    access_token: str
    latest_session: int

    def __init__(self, logger: Logger, access_token: str, latest_session: int) -> None:
        self.logger = logger
        self.access_token = access_token
        self.latest_session = latest_session

    async def __call__(self) -> list[PvpDataSchema]:

        _2s, _3s, rbg = await gather(
            self.fetch_data(bracket=BracketsEnum._2s.value),
            self.fetch_data(bracket=BracketsEnum._3s.value),
            self.fetch_data(bracket=BracketsEnum.rbg.value),
        )

        return [
            *self.clean_data(raw_data=_2s, bracket=BracketsEnum._2s.value),
            *self.clean_data(raw_data=_3s, bracket=BracketsEnum._3s.value),
            *self.clean_data(raw_data=rbg, bracket=BracketsEnum.rbg.value),
        ]

    def refactor_endpoint(self, bracket: str) -> str:
        return (
            PVP_RATING_API.replace("{session}", str(self.latest_session))
            .replace("{bracket}", bracket)
            .replace("{accessToken}", self.access_token)
        )

    async def fetch_data(self, bracket: str) -> list[dict]:

        endpoint = self.refactor_endpoint(bracket=bracket)

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
            raise CouldNotFetchError("The server did not returned an OK response while fetching the pvp data.")

    def clean_data(self, raw_data: list[dict], bracket: str) -> list[PvpDataSchema]:
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
                    bracket=bracket,
                    # avatar_icon=None,
                    session=self.latest_session,
                    # wow_class=None,
                    # wow_spec=None,
                ),
                raw_data,
            )
        )


@re_try(MAX_RETRIES)
async def fetch_pvp_data(logger: Logger, access_token: str, latest_session: int) -> list[PvpDataSchema]:
    await logger.info("2: Fetching wow pvp data...")
    handler = FetchHandler(logger=logger, access_token=access_token, latest_session=latest_session)
    response = await handler()
    await logger.info("Wow pvp data fetched successfully!")
    return response
