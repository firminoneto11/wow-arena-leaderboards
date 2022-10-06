from asyncio import gather, sleep, create_task
from typing import Final, TypedDict, Literal
from dataclasses import dataclass
from itertools import chain

from httpx import AsyncClient, ConnectError, ConnectTimeout, Response

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
from .fetch_pvp_data import PvpDataType
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
    pvp_data: PvpDataType

    divided_workload = []

    def __init__(self, logger: Logger, access_token: str, pvp_data: PvpDataType) -> None:
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
    ) -> tuple[Response, EndpointDataInterface]:
        try:
            return await client.get(endpoint_data["endpoint"]), endpoint_data
        except (ConnectError, ConnectTimeout) as err:
            raise CouldNotFetchError(f"A '{err.__class__.__name__}' occurred while fetching an endpoint.") from err

    def process_responses(
        self,
        unique_players_map: dict[int, UniquePlayerDataclass],
        responses: list[tuple[Response, EndpointDataInterface]],
    ) -> None:

        for (resp, endpoint_data) in responses:
            unique_player = unique_players_map[endpoint_data["blizzard_id"]]

            if resp.status_code == 200:
                data: dict = resp.json()

                if endpoint_data["which"] == "profile":
                    unique_player.class_id = int(data["character_class"]["id"])
                    unique_player.spec_id = int(data["active_spec"]["id"])
                elif endpoint_data["which"] == "media":
                    url: str = data["assets"][0]["value"]
                    unique_player.avatar_icon = url

                continue

            which_data = f"{endpoint_data['which']} data"
            create_task(
                self.logger.warning(
                    f"The server did not returned an OK response while fetching {which_data} for the "
                    f"'{endpoint_data['name']}-{endpoint_data['realm']}' player."
                )
            )

    async def make_requests(
        self, unique_players_map: dict[int, UniquePlayerDataclass], endpoints: list[EndpointDataInterface]
    ) -> None:

        TOTAL_AMOUNT_OF_REQUESTS: Final[int] = len(endpoints)

        responses = []

        # Starting an async client and starting the requests
        async with AsyncClient(timeout=TIMEOUT) as client:
            if TOTAL_AMOUNT_OF_REQUESTS <= REQUESTS_PER_SEC:
                coroutines = [self.fetch(endpoint_data=endpoint_data, client=client) for endpoint_data in endpoints]
                responses.extend(await gather(*coroutines))
            else:
                coroutines, count = [], 0
                for endpoint_data in endpoints:

                    if count == REQUESTS_PER_SEC and coroutines:
                        await self.logger.info(f"Dispatching {len(coroutines)} requests")
                        responses.extend(await gather(*coroutines))
                        await sleep(DELAY)
                        coroutines, count = [], 0

                    coroutines.append(self.fetch(endpoint_data=endpoint_data, client=client))
                    count += 1

                if coroutines:
                    await self.logger.info(f"Dispatching {len(coroutines)} requests")
                    responses.extend(await gather(*coroutines))

        # Processing and returning
        return self.process_responses(unique_players_map=unique_players_map, responses=responses)

    async def __call__(self) -> PvpDataType:

        # Splitting the data for fast access
        players_map: dict[int, dict[str, PvpDataSchema]] = dict()

        for player in self.pvp_data["_2s"]:
            players_map[player.blizzard_id] = dict()
            players_map[player.blizzard_id].update({"_2s": player})

        for player in self.pvp_data["_3s"]:
            if player.blizzard_id not in players_map:
                players_map[player.blizzard_id] = dict()

            players_map[player.blizzard_id].update({"_3s": player})

        for player in self.pvp_data["rbg"]:
            if player.blizzard_id not in players_map:
                players_map[player.blizzard_id] = dict()

            players_map[player.blizzard_id].update({"rbg": player})

        # Creating a hash map with UniquePlayerDataclass only
        unique_players_map: dict[int, UniquePlayerDataclass] = dict()
        for key in players_map:
            player_dict = players_map[key]
            first_key = tuple(player_dict.keys())[0]
            player = player_dict[first_key]

            unique_players_map[player.blizzard_id] = UniquePlayerDataclass(
                blizzard_id=player.blizzard_id, realm=player.realm, name=player.name
            )

        await self.logger.info(
            f"Total amount of unique players to request after the remapping: {len(unique_players_map)}"
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
                    for player in unique_players_map.values()
                ]
            )
        )

        await self.logger.info(f"Total amount of requests to be dispatched: {len(endpoints)}")

        await self.make_requests(unique_players_map=unique_players_map, endpoints=endpoints)

        # Updating the lists with the fetched data
        def set_attributes(original: PvpDataSchema, new: UniquePlayerDataclass) -> None:
            original.class_id = new.class_id
            original.spec_id = new.spec_id
            original.avatar_icon = new.avatar_icon

        for key in unique_players_map:
            unique_player = unique_players_map[key]
            player = players_map[key]

            [set_attributes(original=player[p_key], new=unique_player) for p_key in player]

        return self.pvp_data


async def fetch_wow_media(logger: Logger, access_token: str, pvp_data: PvpDataType) -> PvpDataType:
    await logger.info("5: Fetching the media data from the wow players...")
    handler = FetchWowMediaHandler(logger=logger, access_token=access_token, pvp_data=pvp_data)
    response = await handler()
    await logger.info("Media data fetching completed successfully!")
    return response
