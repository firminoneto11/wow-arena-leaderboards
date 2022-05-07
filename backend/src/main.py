from fastapi import FastAPI
from utils import migrate
from tasks import fetcher
from time import time


api = FastAPI()


@api.on_event("startup")
async def startup():
    inicio = time()
    await migrate()
    await fetcher()
    total = time() - inicio
    print(f"\nDemorou {total:.2f} segundos para fazer todos os fetches e inicar o sistema!\n")


@api.on_event("shutdown")
async def shutdown():
    pass


@api.get("/")
async def root():
    return {"detail": "Hello World"}
