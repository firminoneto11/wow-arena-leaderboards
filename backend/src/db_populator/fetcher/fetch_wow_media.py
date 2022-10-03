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

            which_data = "profile data" if endpoint_data["which"] == "profile" else "media data"
            create_task(
                self.logger.warning(
                    f"The server did not returned an OK response while fetching {which_data} for the "
                    f"'{endpoint_data['name']}-{endpoint_data['realm']}' player."
                )
            )

    async def make_requests(
        self, unique_players_map: dict[int, UniquePlayerDataclass], endpoints: list[EndpointDataInterface]
    ) -> None:

        # TODO: Remove this later
        # TODO: Create methods to divide and conquer
        endpoints = endpoints[:100]

        TOTAL_AMOUNT_OF_REQUESTS: Final[int] = len(endpoints)

        # Starting an async client and starting the requests
        async with AsyncClient(timeout=TIMEOUT) as client:

            if TOTAL_AMOUNT_OF_REQUESTS <= REQUESTS_PER_SEC:
                coroutines = [self.fetch(endpoint_data=endpoint_data, client=client) for endpoint_data in endpoints]
                responses = await gather(*coroutines)
            else:
                responses = []

        # Processing and returning
        return self.process_responses(unique_players_map=unique_players_map, responses=responses)

        # -- TESTING --
        print(f"Len do unique_players pré divisão: {len(unique_players)}")
        unique_players_lists = self.divide_workload(workload=unique_players)
        print(f"Len do unique_players pós divisão: {len(unique_players)}")
        print(f"Total de listas: {len(unique_players_lists)}")
        somatorio = 0
        for l in unique_players_lists:
            somatorio += len(l)
        print(f"Total de requests dps do split: {somatorio}\n")
        # -- TESTING --

        responses = await self.fetch_em_all(lists=unique_players_lists, client=client)

        # -- TESTING --
        print(f"\n# Total de requests respondidas pós divisão: {len(responses)}")
        # -- TESTING --

        if responses:
            responses: list[dict] = [response.json() for response in responses if response.status_code == 200]
        for response in responses:
            blizz_id = int(response["id"])
            class_id = int(response["character_class"]["id"])
            spec_id = int(response["active_spec"]["id"])
            for player in unique_players_copy:
                if player.blizz_id == blizz_id:
                    player.class_id = class_id
                    player.spec_id = spec_id
                    break

        # Esperando pra não tomar throtlle da api da blizz
        print(f"\nEsperando {DELAY} segundos para anti-throttle. Fetch de avatares!\n")
        await sleep(DELAY)

        # Fazendo um fetch para cada jogador único para pegar o link do avatar de cada um pois o avatar é o mesmo independente da
        # bracket
        responses = []
        if unique_players_lists is None:  # Se cair aqui é pq não teve divisão de requests
            for player in unique_players_copy:
                endpoint = self.refactor_endpoint(tipo="char-media", realm=player.realm, name=player.name.lower())
                responses.append(client.get(endpoint))
            responses = await gather(*responses)
        else:
            responses = await self.fetch_em_all(lists=unique_players_lists, client=client, is_avatar=True)
            print(f"\n# Total de requests respondidas pós divisão: {len(responses)}")
        if responses:
            responses: list[dict] = [response.json() for response in responses if response.status_code == 200]
        for response in responses:
            blizz_id = int(response["character"]["id"])
            avatar_icon: str = response["assets"][0]["value"]
            for player in unique_players_copy:
                if player.blizz_id == blizz_id:
                    player.avatar_icon = avatar_icon
                    break

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

        await self.logger.info(f"Total amount of requests to be executed: {len(endpoints)}")

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

    def divide_workload(self, workload: list[UniquePlayerDataclass]) -> list[list[UniquePlayerDataclass]]:
        helper_list = []
        counter = 0
        if len(workload) <= REQUESTS_PER_SEC:
            for _ in range(len(workload)):
                helper_list.append(workload.pop())
            self.divided_workload.append(helper_list)
            return self.divided_workload
        else:
            for _ in range(REQUESTS_PER_SEC):
                helper_list.append(workload.pop())
                counter += 1
            self.divided_workload.append(helper_list)
            return self.divide_workload(workload=workload)

    async def fetch_em_all(self, lists: list[list[UniquePlayerDataclass]], client: AsyncClient, is_avatar=False):
        responses_helper = []
        for idx, _list in enumerate(lists):

            def get_new_awaitables(lista, cliente):
                anti_throttle = []
                for player in lista:
                    endpoint = self.refactor_endpoint(
                        tipo="char-media" if is_avatar else "profile", realm=player.realm, name=player.name.lower()
                    )
                    anti_throttle.append(cliente.get(endpoint))
                return anti_throttle

            gather_return = None
            for idx in range(MAX_RETRIES):
                anti_throttle = get_new_awaitables(lista=_list, cliente=client)
                total_de_reqs = len(anti_throttle)

                try:
                    print(
                        f"\nTentando realizar o fetch de {total_de_reqs} jogadores. {idx + 1}/{MAX_RETRIES} tentativas."
                    )
                    gather_return = await gather(*anti_throttle)
                except ConnectError:
                    if idx == MAX_RETRIES:
                        print(f"\nÚltima tentativa realizada sem sucesso.")
                        if is_avatar:
                            print(f"Dados de avatares não foram coletados para {total_de_reqs} jogadores.")
                        else:
                            print(f"Dados de class/spec não foram coletados para {total_de_reqs} jogadores.")
                    continue
                else:
                    print("Fetch efetuado com sucesso!")
                    break

            if gather_return is not None:
                responses_helper.append(gather_return)

            if idx != len(lists) - 1:
                print(f"\nEsperando {DELAY} segundos para não tomar throttle. Anti Throttle mechanism!\n")
                await sleep(DELAY)

        return list(chain(*responses_helper))


async def fetch_wow_media(logger: Logger, access_token: str, pvp_data: PvpDataType) -> PvpDataType:
    await logger.info("5: Fetching the media data from the wow players...")
    handler = FetchWowMediaHandler(logger=logger, access_token=access_token, pvp_data=pvp_data)
    response = await handler()
    await logger.info("Media data fetching completed successfully!")
    return response
