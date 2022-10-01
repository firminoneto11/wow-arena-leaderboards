from typing import Final
from copy import copy as shallow_copy
from asyncio import gather, sleep
from dataclasses import dataclass
from itertools import chain

from httpx import AsyncClient, ConnectError, ConnectTimeout

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

    async def __call__(self):

        # Splitting the data
        _2s = self.pvp_data["_2s"]
        _3s = self.pvp_data["_3s"]
        rbg = self.pvp_data["rbg"]

        # TODO: Create a hash map that contains lists pointing to the original data

        # Creating a hash map with the unique players only
        unique_players_map = {
            player.blizzard_id: UniquePlayerDataclass(
                blizzard_id=player.blizzard_id, realm=player.realm, name=player.name
            )
            for player in _2s
        }

        for player in _3s:
            if player.blizzard_id not in unique_players_map:
                unique_players_map[player.blizzard_id] = UniquePlayerDataclass(
                    blizzard_id=player.blizzard_id, realm=player.realm, name=player.name
                )

        for player in rbg:
            if player.blizzard_id not in unique_players_map:
                unique_players_map[player.blizzard_id] = UniquePlayerDataclass(
                    blizzard_id=player.blizzard_id, realm=player.realm, name=player.name
                )

        TOTAL_AMOUNT_OF_REQUESTS: Final[int] = len(unique_players_map)

        await self.logger.info(f"Total amount of players to request after remapping: {TOTAL_AMOUNT_OF_REQUESTS}")
        await self.logger.info(f"Amount of 2s players: {len(_2s)}")
        await self.logger.info(f"Amount of 3s players: {len(_3s)}")
        await self.logger.info(f"Amount of rbg players: {len(rbg)}")

        # Copying the unique players map to have references in memory
        unique_players_copy = shallow_copy(unique_players_map)

        return

        # Starting an async client and starting the requests
        async with AsyncClient(timeout=TIMEOUT) as client:

            responses = []

            if TOTAL_AMOUNT_OF_REQUESTS <= REQUESTS_PER_SEC:

                for player in unique_players_map.values():
                    endpoint = self.refactor_endpoint(realm=player.realm, name=player.name.lower())
                    responses.append(client.get(endpoint))
                responses = await gather(*responses)

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

        # Updating the lists with the fetched data
        for unique_player in unique_players_copy.values():
            for player in _2s:
                if player.blizzard_id == unique_player.blizzard_id:
                    player.class_id = unique_player.class_id
                    player.spec_id = unique_player.spec_id
                    player.avatar_icon = unique_player.avatar_icon
                    break
            for player in _3s:
                if player.blizzard_id == unique_player.blizzard_id:
                    player.class_id = unique_player.class_id
                    player.spec_id = unique_player.spec_id
                    player.avatar_icon = unique_player.avatar_icon
                    break
            for player in rbg:
                if player.blizzard_id == unique_player.blizzard_id:
                    player.class_id = unique_player.class_id
                    player.spec_id = unique_player.spec_id
                    player.avatar_icon = unique_player.avatar_icon
                    break

        return {
            "_2s": _2s,
            "_3s": _3s,
            "rbg": rbg,
        }


async def fetch_wow_media(logger: Logger, access_token: str, pvp_data: PvpDataType) -> PvpDataType:
    await logger.info("5: Fetching the media data from the wow players...")
    handler = FetchWowMediaHandler(logger=logger, access_token=access_token, pvp_data=pvp_data)
    response = await handler()
    await logger.info("Media data fetching completed successfully!")
    return response
