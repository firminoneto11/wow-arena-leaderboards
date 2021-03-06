from settings import PROFILE_API, CHAR_MEDIA_API, TIMEOUT, DELAY, REQUESTS_PER_SEC, MAX_RETRIES
from httpx import AsyncClient, ConnectError
from utils import PvpDataDataclass
from typing import List, Dict
from asyncio import gather, sleep
from itertools import chain
from dataclasses import dataclass


@dataclass
class UniquePlayerDataclass:
    blizz_id: int
    realm: str
    name: str
    class_id = None
    spec_id = None
    avatar_icon = None


class FetchWowMedia:

    access_token: str
    pvp_data: Dict[str, List[PvpDataDataclass]]
    divided_workload = []

    async def run(self, access_token: str, pvp_data: Dict[str, List[PvpDataDataclass]]):
        self.access_token = access_token
        self.pvp_data = pvp_data
        self.pvp_data = await self.update_data()

        return self.pvp_data

    def refactor_endpoint(self, tipo: str = "profile", *args, **kwargs):
        match tipo:
            case "profile":
                return PROFILE_API.replace("${accessToken}", self.access_token).replace(
                    "${realm_slug}", kwargs.get("realm")
                ).replace("${char_name}", kwargs.get("name"))
            case "char-media":
                return CHAR_MEDIA_API.replace("${accessToken}", self.access_token).replace(
                    "${realm_slug}", kwargs.get("realm")
                ).replace("${char_name}", kwargs.get("name"))

    def divide_workload(self, workload: List[UniquePlayerDataclass]) -> List[List[UniquePlayerDataclass]]:
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

    async def fetch_em_all(self, lists: List[List[UniquePlayerDataclass]], client: AsyncClient, is_avatar=False):
        responses_helper = []
        for idx, _list in enumerate(lists):

            def get_new_awaitables(lista, cliente):
                anti_throttle = []
                for player in lista:
                    endpoint = self.refactor_endpoint(
                        tipo="char-media" if is_avatar else "profile",
                        realm=player.realm, name=player.name.lower()
                    )
                    anti_throttle.append(cliente.get(endpoint))
                return anti_throttle

            gather_return = None
            for idx in range(MAX_RETRIES):
                anti_throttle = get_new_awaitables(lista=_list, cliente=client)
                total_de_reqs = len(anti_throttle)

                try:
                    print(f"\nTentando realizar o fetch de {total_de_reqs} jogadores. {idx + 1}/{MAX_RETRIES} tentativas.")
                    gather_return = await gather(*anti_throttle)
                except ConnectError:
                    if idx == MAX_RETRIES:
                        print(f"\n??ltima tentativa realizada sem sucesso.")
                        if is_avatar:
                            print(f"Dados de avatares n??o foram coletados para {total_de_reqs} jogadores.")
                        else:
                            print(f"Dados de class/spec n??o foram coletados para {total_de_reqs} jogadores.")
                    continue
                else:
                    print("Fetch efetuado com sucesso!")
                    break

            if gather_return is not None:
                responses_helper.append(gather_return)

            if idx != len(lists) - 1:
                print(f"\nEsperando {DELAY} segundos para n??o tomar throttle. Anti Throttle mechanism!\n")
                await sleep(DELAY)

        return list(chain(*responses_helper))

    async def update_data(self) -> Dict[str, List[PvpDataDataclass]]:

        # Separando os dados
        twos = self.pvp_data["twos"]
        thres = self.pvp_data["thres"]
        rbg = self.pvp_data["rbg"]

        # Criando uma lista somente com jogadores ??nicos
        unique_players = [
            UniquePlayerDataclass(blizz_id=player.blizz_id, realm=player.realm, name=player.name)
            for player in twos
        ]

        # Iterando na lista de jogadores da bracket de 3s e checando se o jogador se encontra na lista de jogadores ??nicos. Caso ele n??o
        # se encontre ele ?? adicionado
        for player in thres:
            pl = UniquePlayerDataclass(blizz_id=player.blizz_id, realm=player.realm, name=player.name)
            if pl not in unique_players:
                unique_players.append(pl)

        # Iterando na lista de jogadores da bracket de rbg e checando se o jogador se encontra na lista de jogadores ??nicos. Caso ele 
        # n??o se encontre ele ?? adicionado
        for player in rbg:
            pl = UniquePlayerDataclass(blizz_id=player.blizz_id, realm=player.realm, name=player.name)
            if pl not in unique_players:
                unique_players.append(pl)

        # Copiando a lista de unique_players para ter duas refer??ncias na mem??ria
        unique_players_copy = unique_players.copy()

        # Fazendo um fetch para pegar a classe e a spec de cada jogador ??nico pois a spec e classe s??o as mesmas independente da bracket
        async with AsyncClient(timeout=TIMEOUT) as client:
            responses = []
            total_de_requests = len(unique_players)
            unique_players_lists = None
            if total_de_requests <= REQUESTS_PER_SEC:
                for player in unique_players:
                    endpoint = self.refactor_endpoint(realm=player.realm, name=player.name.lower())
                    responses.append(client.get(endpoint))
                responses = await gather(*responses)
            else:

                # -- TESTING --
                print(f"Len do unique_players pr?? divis??o: {len(unique_players)}")
                unique_players_lists = self.divide_workload(workload=unique_players)
                print(f"Len do unique_players p??s divis??o: {len(unique_players)}")
                print(f"Total de listas: {len(unique_players_lists)}")
                somatorio = 0
                for l in unique_players_lists:
                    somatorio += len(l)
                print(f"Total de requests dps do split: {somatorio}\n")
                # -- TESTING --

                responses = await self.fetch_em_all(lists=unique_players_lists, client=client)

                # -- TESTING -- 
                print(f"\n# Total de requests respondidas p??s divis??o: {len(responses)}")
                # -- TESTING -- 

            if responses:
                responses: List[dict] = [response.json() for response in responses if response.status_code == 200]
            for response in responses:
                blizz_id = int(response["id"])
                class_id = int(response["character_class"]["id"])
                spec_id = int(response["active_spec"]["id"])
                for player in unique_players_copy:
                    if player.blizz_id == blizz_id:
                        player.class_id = class_id
                        player.spec_id = spec_id
                        break

            # Esperando pra n??o tomar throtlle da api da blizz
            print(f"\nEsperando {DELAY} segundos para anti-throttle. Fetch de avatares!\n")
            await sleep(DELAY)

            # Fazendo um fetch para cada jogador ??nico para pegar o link do avatar de cada um pois o avatar ?? o mesmo independente da
            # bracket
            responses = []
            if unique_players_lists is None:  # Se cair aqui ?? pq n??o teve divis??o de requests
                for player in unique_players_copy:
                    endpoint = self.refactor_endpoint(tipo="char-media", realm=player.realm, name=player.name.lower())
                    responses.append(client.get(endpoint))
                responses = await gather(*responses)
            else:
                responses = await self.fetch_em_all(lists=unique_players_lists, client=client, is_avatar=True)
                print(f"\n# Total de requests respondidas p??s divis??o: {len(responses)}")
            if responses:
                responses: List[dict] = [response.json() for response in responses if response.status_code == 200]
            for response in responses:
                blizz_id = int(response["character"]["id"])
                avatar_icon: str = response["assets"][0]["value"]
                for player in unique_players_copy:
                    if player.blizz_id == blizz_id:
                        player.avatar_icon = avatar_icon
                        break

        # Atualizando as listas com os dados que foram buscados pelo fetch
        for unique_player in unique_players_copy:
            for player in twos:
                if player.blizz_id == unique_player.blizz_id:
                    player.class_id = unique_player.class_id
                    player.spec_id = unique_player.spec_id
                    player.avatar_icon = unique_player.avatar_icon
                    break
            for player in thres:
                if player.blizz_id == unique_player.blizz_id:
                    player.class_id = unique_player.class_id
                    player.spec_id = unique_player.spec_id
                    player.avatar_icon = unique_player.avatar_icon
                    break
            for player in rbg:
                if player.blizz_id == unique_player.blizz_id:
                    player.class_id = unique_player.class_id
                    player.spec_id = unique_player.spec_id
                    player.avatar_icon = unique_player.avatar_icon
                    break

        return { "twos": twos, "thres": thres, "rbg": rbg }
