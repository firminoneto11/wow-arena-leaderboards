from copy import copy as shallow_copy
from asyncio import gather, sleep
from dataclasses import dataclass
from itertools import chain
from typing import Final

from httpx import AsyncClient, ConnectError, ConnectTimeout, Response

from shared import Logger, re_try
from .fetch_pvp_data import PvpDataType
from db_populator.constants import (
    PROFILE_API,
    CHAR_MEDIA_API,
    TIMEOUT,
    DELAY,
    REQUESTS_PER_SEC,
    MAX_RETRIES,
)
from ..schemas import PvpDataSchema
from ..exceptions import CouldNotFetchError


@dataclass
class UniquePlayerDataclass:
    blizzard_id: int
    realm: str
    name: str
    class_id: int | None = None
    spec_id: int | None = None
    avatar_icon: str | None = None


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
                    PROFILE_API.replace("${accessToken}", self.access_token)
                    .replace("${realmSlug}", realm)
                    .replace("${charName}", name)
                )
            case "media":
                return (
                    CHAR_MEDIA_API.replace("${accessToken}", self.access_token)
                    .replace("${realmSlug}", realm)
                    .replace("${charName}", name)
                )

    @re_try(MAX_RETRIES)
    async def fetch(self, endpoint: str, client: AsyncClient, which: str) -> tuple[Response, str]:
        try:
            return client.get(endpoint), which
        except (ConnectError, ConnectTimeout) as err:
            raise CouldNotFetchError(f"A '{err.__class__.__name__}' occurred while fetching an endpoint.") from err

    async def make_requests(
        self,
        players_map: dict[int, dict[str, PvpDataSchema]],
        unique_players_map: dict[int, UniquePlayerDataclass],
    ) -> None:
        # Starting an async client and starting the requests
        async with AsyncClient(timeout=TIMEOUT) as client:

            if TOTAL_AMOUNT_OF_REQUESTS <= REQUESTS_PER_SEC:

                endpoints: list[str] = [
                    self.refactor_endpoint(realm=player.realm.lower(), name=player.name.lower())
                    for player in unique_players_copy.values()
                ]

                responses: list[Response] = await gather(
                    *[self.fetch(endpoint=endpoint, client=client) for endpoint in endpoints]
                )

            else:

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

        TOTAL_AMOUNT_OF_UNIQUE_PLAYERS: Final[int] = len(unique_players_map)

        await self.logger.info(
            f"Total amount of unique players to request after remapping: {TOTAL_AMOUNT_OF_UNIQUE_PLAYERS}"
        )

        count = [len(players_map[key]) for key in players_map]
        total_bracket_records = len(self.pvp_data["_2s"]) + len(self.pvp_data["_3s"]) + len(self.pvp_data["rbg"])

        await self.logger.info(
            f"Total records amount in all 3 brackets is correct? {sum(count) == total_bracket_records}. {total_bracket_records}"
        )

        await self.make_requests(players_map=players_map, unique_players_map=unique_players_map)

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
