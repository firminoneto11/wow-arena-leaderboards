from settings import PROFILE_API, CHAR_MEDIA_API, TIMEOUT, DELAY, REQUESTS_PER_SEC
from httpx import AsyncClient
from utils import PvpDataDataclass
from typing import List, Dict
from asyncio import gather, sleep
from itertools import chain


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

    def divide_workload(self, workload: List[PvpDataDataclass]) -> List[List[PvpDataDataclass]]:
        helper_list = []
        counter = 0
        if len(workload) <= REQUESTS_PER_SEC:
            self.divided_workload.append(workload)
            return self.divided_workload
        else:
            for _ in range(REQUESTS_PER_SEC):
                helper_list.append(workload.pop())
                counter += 1
            self.divided_workload.append(helper_list)
            return self.divide_workload(workload=workload)

    async def update_data(self) -> Dict[str, List[PvpDataDataclass]]:

        # Separando os dados
        twos = self.pvp_data["twos"]
        thres = self.pvp_data["thres"]
        rbg = self.pvp_data["rbg"]

        # Criando uma lista somente com jogadores únicos
        unique_players = [*twos]

        # Iterando na lista de jogadores da bracket de 3s e checando se o jogador se encontra na lista de jogadores únicos. Caso ele não
        # se encontre ele é adicionado
        for player in thres:
            is_in_list = False
            for unique_player in unique_players:
                if unique_player.blizz_id == player.blizz_id:
                    is_in_list = True
                    break
            if not is_in_list:
                unique_players.append(player)

        # Iterando na lista de jogadores da bracket de rbg e checando se o jogador se encontra na lista de jogadores únicos. Caso ele 
        # não se encontre ele é adicionado
        for player in rbg:
            is_in_list = False
            for unique_player in unique_players:
                if unique_player.blizz_id == player.blizz_id:
                    is_in_list = True
                    break
            if not is_in_list:
                unique_players.append(player)

        # Fazendo um fetch para pegar a classe e a spec de cada jogador único pois a spec e classe são as mesmas independente da bracket
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
                print(f"Total de requests: {total_de_requests}")
                unique_players_lists = self.divide_workload(workload=unique_players)
                print(f"Total de listas: {len(unique_players_lists)}")
                somatorio = 0
                for l in unique_players_lists:
                    somatorio += len(l)
                print(f"Total de requests dps do split: {somatorio}\n")
                # -- TESTING --

                responses_helper = []
                for idx, _list in enumerate(unique_players_lists):
                    anti_throttle = []
                    for player in _list:
                        endpoint = self.refactor_endpoint(realm=player.realm, name=player.name.lower())
                        anti_throttle.append(client.get(endpoint))
                    print(f"Fazendo fetch de {len(anti_throttle)} jogadores")
                    responses_helper.append(await gather(*anti_throttle))
                    if idx != len(unique_players_lists) - 1:
                        print(f"\nEsperando {DELAY} segundos para não tomar throttle. Anti Throttle mechanism!\n")
                        await sleep(DELAY)
                responses = list(chain(*responses_helper))

                # -- TESTING -- 
                print(f"\n# Total de requests respondidas no helper: {len(responses)}")
                # -- TESTING -- 

            responses: List[dict] = [response.json() for response in responses if response.status_code == 200]
            for response in responses:
                blizz_id: int = response["id"]
                class_id: int = response["character_class"]["id"]
                spec_id: int = response["active_spec"]["id"]
                for player in unique_players:
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
            print(f"Realizando {len(unique_players)} requisições")
            for player in unique_players:
                endpoint = self.refactor_endpoint(tipo="char-media", realm=player.realm, name=player.name.lower())
                responses.append(client.get(endpoint))
            responses = await gather(*responses)
            responses: List[dict] = [response.json() for response in responses if response.status_code == 200]
            for response in responses:
                blizz_id: int = response["character"]["id"]
                avatar_icon: str = response["assets"][0]["value"]
                for player in unique_players:
                    if player.blizz_id == blizz_id:
                        player.avatar_icon = avatar_icon
                        break

        # Atualizando as listas com os dados que foram buscados pelo fetch
        for unique_player in unique_players:
            for player in twos:
                if player.blizz_id == unique_player.blizz_id:
                    player.class_id = unique_player.class_id
                    player.spec_id = unique_player.spec_id
                    player.avatar_icon = avatar_icon
                    break
            for player in thres:
                if player.blizz_id == unique_player.blizz_id:
                    player.class_id = unique_player.class_id
                    player.spec_id = unique_player.spec_id
                    player.avatar_icon = avatar_icon
                    break
            for player in rbg:
                if player.blizz_id == unique_player.blizz_id:
                    player.class_id = unique_player.class_id
                    player.spec_id = unique_player.spec_id
                    player.avatar_icon = avatar_icon
                    break

        return { "twos": twos, "thres": thres, "rbg": rbg }