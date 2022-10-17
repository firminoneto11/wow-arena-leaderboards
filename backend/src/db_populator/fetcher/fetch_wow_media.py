from asyncio import Future, Task, as_completed, sleep, create_task
from typing import Final, Iterator, TypedDict, Literal
from dataclasses import dataclass
from itertools import chain

from httpx import AsyncClient, ConnectError, ConnectTimeout

from shared import Logger, re_try
from db_populator.constants import (
    PROFILE_API,
    CHAR_MEDIA_API,
    TIMEOUT,
    DELAY,
    REQUESTS_PER_SEC,
    MAX_RETRIES,
)
from ..exceptions import CouldNotFetchError
from .utils import filter_pvp_data_list
from ..schemas import PvpDataSchema


@dataclass
class UniquePlayerDataclass:
    blizzard_id: int
    realm: str
    name: str
    class_id: int | None = None
    spec_id: int | None = None
    avatar_icon: str | None = None


class EndpointDataInterface(TypedDict):
    blizzard_id: int
    name: str
    realm: str
    which: Literal["profile"] | Literal["media"]
    endpoint: str


class FetchWowMediaHandler:

    logger: Logger
    access_token: str
    pvp_data: list[PvpDataSchema]
    unique_players_map: dict[int, UniquePlayerDataclass]

    divided_workload = []

    def __init__(self, logger: Logger, access_token: str, pvp_data: list[PvpDataSchema]) -> None:
        self.logger = logger
        self.access_token = access_token
        self.pvp_data = pvp_data

    def refactor_endpoint(self, which: str, realm: str, name: str) -> str:
        match which:
            case "profile":
                return (
                    PROFILE_API.replace("{accessToken}", self.access_token)
                    .replace("{realmSlug}", realm)
                    .replace("{charName}", name)
                )
            case "media":
                return (
                    CHAR_MEDIA_API.replace("{accessToken}", self.access_token)
                    .replace("{realmSlug}", realm)
                    .replace("{charName}", name)
                )

    @re_try(MAX_RETRIES)
    async def fetch(
        self, endpoint_data: EndpointDataInterface, client: AsyncClient
    ) -> tuple[dict, EndpointDataInterface] | None:
        try:
            response = await client.get(endpoint_data["endpoint"])
            if response.status_code == 200:
                return response.json(), endpoint_data
            create_task(
                self.logger.warning(
                    f"The server did not returned an OK response while fetching {endpoint_data['which']} data for the "
                    f"'{endpoint_data['name']}-{endpoint_data['realm']}' player."
                )
            )
        except (ConnectError, ConnectTimeout) as err:
            raise CouldNotFetchError(f"A '{err.__class__.__name__}' occurred while fetching an endpoint.") from err

    async def fetch_and_process(self, tasks: list[Task]) -> None:
        as_completed_generator: Iterator[Future[tuple[dict, EndpointDataInterface] | None]] = as_completed(tasks)
        for future in as_completed_generator:
            contents = await future
            if contents:

                data, endpoint_data = contents
                unique_player = self.unique_players_map[endpoint_data["blizzard_id"]]

                if endpoint_data["which"] == "profile":
                    unique_player.class_id = int(data["character_class"]["id"])
                    unique_player.spec_id = int(data["active_spec"]["id"])
                elif endpoint_data["which"] == "media":
                    url: str = data["assets"][0]["value"]
                    unique_player.avatar_icon = url

    async def make_requests(self, endpoints: list[EndpointDataInterface]) -> None:

        TOTAL_AMOUNT_OF_REQUESTS: Final[int] = len(endpoints)

        # Starting an async client and starting the requests
        async with AsyncClient(timeout=TIMEOUT) as client:
            if TOTAL_AMOUNT_OF_REQUESTS <= REQUESTS_PER_SEC:
                tasks = [
                    create_task(self.fetch(endpoint_data=endpoint_data, client=client)) for endpoint_data in endpoints
                ]
                return await self.fetch_and_process(tasks=tasks)

            tasks, count = [], 0
            for endpoint_data in endpoints:

                if count == REQUESTS_PER_SEC and tasks:
                    await self.logger.info(f"Dispatching {len(tasks)} requests")
                    await self.fetch_and_process(tasks=tasks)
                    await sleep(DELAY)
                    tasks, count = [], 0

                tasks.append(create_task(self.fetch(endpoint_data=endpoint_data, client=client)))
                count += 1

            if tasks:
                await self.logger.info(f"Dispatching {len(tasks)} requests")
                await self.fetch_and_process(tasks=tasks)

    async def __call__(self) -> list[PvpDataSchema]:

        _2s, _3s, rbg = filter_pvp_data_list(data=self.pvp_data)

        # Splitting the data for fast access
        players_map: dict[int, dict[str, PvpDataSchema]] = dict()

        for player in _2s:
            players_map[player.blizzard_id] = dict()
            players_map[player.blizzard_id].update({"_2s": player})

        for player in _3s:
            if player.blizzard_id not in players_map:
                players_map[player.blizzard_id] = dict()

            players_map[player.blizzard_id].update({"_3s": player})

        for player in rbg:
            if player.blizzard_id not in players_map:
                players_map[player.blizzard_id] = dict()

            players_map[player.blizzard_id].update({"rbg": player})

        # Creating a hash map with UniquePlayerDataclass only
        self.unique_players_map = dict()

        for key in players_map:
            player_dict = players_map[key]
            first_key = tuple(player_dict.keys())[0]
            player = player_dict[first_key]

            self.unique_players_map[player.blizzard_id] = UniquePlayerDataclass(
                blizzard_id=player.blizzard_id, realm=player.realm, name=player.name
            )

        await self.logger.info(
            f"Total amount of unique players to request after the remapping: {len(self.unique_players_map)}"
        )

        endpoints: list[EndpointDataInterface] = list(
            chain(
                *[
                    [
                        {
                            "blizzard_id": player.blizzard_id,
                            "name": player.name,
                            "realm": player.realm,
                            "which": "profile",
                            "endpoint": self.refactor_endpoint(
                                realm=player.realm.lower(), name=player.name.lower(), which="profile"
                            ),
                        },
                        {
                            "blizzard_id": player.blizzard_id,
                            "name": player.name,
                            "realm": player.realm,
                            "which": "media",
                            "endpoint": self.refactor_endpoint(
                                realm=player.realm.lower(), name=player.name.lower(), which="media"
                            ),
                        },
                    ]
                    for player in self.unique_players_map.values()
                ]
            )
        )

        await self.logger.info(f"Total amount of requests to be dispatched: {len(endpoints)}")
        await self.make_requests(endpoints=endpoints)

        # Updating the lists with the fetched data
        def set_attributes(original: PvpDataSchema, new: UniquePlayerDataclass) -> None:
            original.wow_class = new.class_id
            original.wow_spec = new.spec_id
            original.avatar_icon = new.avatar_icon

        for key in self.unique_players_map:
            unique_player = self.unique_players_map[key]
            player = players_map[key]

            [set_attributes(original=player[p_key], new=unique_player) for p_key in player]

        return self.pvp_data


async def fetch_wow_media(logger: Logger, access_token: str, pvp_data: list[PvpDataSchema]) -> list[PvpDataSchema]:
    await logger.info("5: Fetching the media data from the wow players...")
    handler = FetchWowMediaHandler(logger=logger, access_token=access_token, pvp_data=pvp_data)
    response = await handler()
    await logger.info("Media data fetching completed successfully!")
    return response
