from fastapi import FastAPI
from tasks import RetriveBlizzardData


api = FastAPI()


@api.on_event("startup")
async def startup():
    await RetriveBlizzardData.mount_data()


@api.on_event("shutdown")
async def shutdown():
    pass


@api.get("/")
async def root():
    return {"detail": "Hello World"}
