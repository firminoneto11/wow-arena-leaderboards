from fastapi import FastAPI
from tasks import RetrievePvpData


api = FastAPI()


@api.on_event("startup")
async def startup():
    await RetrievePvpData.run()


@api.on_event("shutdown")
async def shutdown():
    pass


@api.get("/")
async def root():
    return {"detail": "Hello World"}


# TODO: Criar outra tabela chamada 'WowClasses'

# TODO: Criar outra tabela chamada 'SpecsWowClasses'

# TODO: No startup da api, fazer um fetch que pega todas as classes

# TODO: No startup da api, fazer um fetch que pega todas as specs

# TODO: No startup da api, fazer fetchs que pegam os ícones de todas as classes

# TODO: No startup da api, fazer fetchs que pega os ícones de todas as specs
