from httpx import AsyncClient
from decouple import config as get_env_var
from settings import (
    TIMEOUT, BLIZZARD_TOKENS_URL
)


class FetchApiToken:

    async def run(self):
        """ Método principal da classe. Retorna um access_token """
        return await self.fetch_token()

    async def fetch_token(self):
        """
        Este método faz uma requisição ao servidor da blizzard para pegar um access token atualizado. Retorna um dicionário contendo 
        informações sobre o processo e a resposta recebida
        """

        resposta = {
            "error": False,
            "token_stuff": "",
            "error_message": ""
        }

        credential_string = get_env_var("ENCODED_CREDENTIALS")
        content_type = "application/x-www-form-urlencoded"

        headers = {
            "Authorization": credential_string,
            "Content-Type": content_type
        }

        body = "grant_type=client_credentials"

        async with AsyncClient(timeout=TIMEOUT) as client:

            response = None

            try:
                response = await client.post(
                    url=BLIZZARD_TOKENS_URL,
                    headers=headers,
                    data=body
                )
            except Exception as error:
                resposta["error"] = True
                resposta["error_message"] = error

            data = response.json()

            if response.status_code == 200:
                resposta["token_stuff"] = data
            else:
                resposta["error"] = True
                resposta["error_message"] = "Status code da response foi diferente de 200. Verificar o ocorrido"

            return resposta
