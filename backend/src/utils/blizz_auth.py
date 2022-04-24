from httpx import AsyncClient
from decouple import config
from settings import BLIZZARD_TOKENS_URL


# Formato do retorno da api da Blizzard
token_stuff = {
    "access_token": str,
    "token_type": str,
    "expires_in": int,
    "sub": str,
}


async def get_token_stuff():
    """ Esta função faz uma requisição ao servidor da blizzard para pegar um access token atualizado """

    credential_string = config("ENCODED_CREDENTIALS")

    headers = {
        "Authorization": credential_string,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    body = "grant_type=client_credentials"

    async with AsyncClient() as client:

        try:
            response = await client.post(
                url=BLIZZARD_TOKENS_URL,
                headers=headers,
                data=body
            )
        except Exception as error:
            print((
                f"\nOcorreu um erro ao pegar o access token da blizzard. Não será possível pegar os dados! "
                f"Mais informações sobre o erro: {error}\n"
            ))
            return

        data = response.json()

        if response.status_code == 200:
            return data
        else:
            print(response)
            print(data)
            raise Exception("Houve um problema no status code ao solicitar o access token")


if __name__ == '__main__':
    from asyncio import run
    run(get_token_stuff())
