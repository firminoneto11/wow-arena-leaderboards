from shared.utils import WowSpecsDataclass
from httpx import AsyncClient
from typing import List
from asyncio import gather
from settings import ALL_SPECS_API, SPEC_MEDIA_API, TIMEOUT


class FetchWowSpecs:

    access_token: str

    async def run(self, access_token: str):
        self.access_token = access_token
        wow_specs: List[WowSpecsDataclass] = await self.get_wow_specs()

        _futures = []
        for wow_spec in wow_specs:
            _futures.append(self.get_icon_for_wow_spec(blizz_id=wow_spec.blizz_id))
        _futures = await gather(*_futures)

        for index, wow_spec in enumerate(wow_specs):
            wow_spec.spec_icon = _futures[index]

        return wow_specs

    def refactor_endpoint(self, tipo: str = "all-specs", *args, **kwargs):
        match tipo:
            case "all-specs":
                return ALL_SPECS_API.replace("${accessToken}", self.access_token)
            case "spec-icon":
                return SPEC_MEDIA_API.replace("${accessToken}", self.access_token).replace(
                    "${spec_id}", str(kwargs.get("blizz_id"))
                )

    async def get_wow_specs(self):

        endpoint = self.refactor_endpoint()

        async with AsyncClient(timeout=TIMEOUT) as client:

            response = await client.get(endpoint)

            data = response.json()

            if response.status_code == 200:
                return self.format_returned_api_data(data=data)
            else:
                raise Exception(f"Houve um problema no status code ao solicitar os dados de todas as specs")

    def format_returned_api_data(self, data: dict):

        instances = []

        for key, val in data.items():
            if key == "character_specializations":
                for wow_spec in val:
                    instances.append(WowSpecsDataclass(blizz_id=wow_spec["id"], spec_name=wow_spec["name"]))

        return instances

    async def get_icon_for_wow_spec(self, blizz_id: int):

        endpoint = self.refactor_endpoint(tipo="spec-icon", blizz_id=blizz_id)

        async with AsyncClient(timeout=TIMEOUT) as client:

            response = await client.get(endpoint)

            data = response.json()

            if response.status_code == 200:
                return data["assets"][0]["value"]
            else:
                raise Exception(
                    f"Houve um problema no status code ao solicitar o ícone para a classe de blizz id {blizz_id}"
                )
