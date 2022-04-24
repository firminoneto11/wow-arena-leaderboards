from asyncio import run, gather
# from connection_layer import objects
# from services.brackets_service import BracketsService as Bs, BracketsEnum
# from services.sessions_service import SessionsService as Ss
from utils.blizz_auth import get_token_stuff
from utils.blizz_data import get_data


async def main():

    token_stuff: dict = await get_token_stuff()

    if token_stuff is not None:

        access_token = token_stuff.get("access_token")

        requests = [
            get_data(session=32, bracket="2v2", access_token=access_token),
            get_data(session=32, bracket="3v3", access_token=access_token),
            # get_data(session=32, bracket="10v10", access_token=access_token),
        ]

        data = await gather(*requests)

        print("\n--2V2--\n")
        lista = data[0]

        for player in lista:
            char = player['character']
            print(f"Nome: {char['name']} | CR: {player['rating']} | Reino: {char['realm']['slug']}")

        print("\n--3V3--\n")
        lista = data[1]

        for player in lista:
            char = player['character']
            print(f"Nome: {char['name']} | CR: {player['rating']} | Reino: {char['realm']['slug']}")


if __name__ == "__main__":
    run(main())

# TODO: Ver como é a bracket de RBG
# TODO: Colocar os dados num dataclass ou pydantic model pra facilitar o acesso de atributos
