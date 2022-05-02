from fastapi import FastAPI
from utils import migrate
from tasks import fetcher


api = FastAPI()


@api.on_event("startup")
async def startup():
    await migrate()
    await fetcher()


@api.on_event("shutdown")
async def shutdown():
    pass


@api.get("/")
async def root():
    return {"detail": "Hello World"}
