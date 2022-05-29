from fastapi import FastAPI, Request, HTTPException
from utils import migrate
from schemas import WowDataSchema
from controllers import DataController
from middlewares import cors_middleware_config


api = FastAPI()
api.add_middleware(**cors_middleware_config)


@api.on_event("startup")
async def startup():
    await migrate()


@api.on_event("shutdown")
async def shutdown():
    pass


@api.get("/data/{bracket}/", response_model=WowDataSchema)
async def data(request: Request, bracket: str):
    match bracket:
        case "3s":
            return await DataController(req=request).get(tp="3v3")
        case "2s":
            return await DataController(req=request).get(tp="2v2")
        case "rbg":
            return await DataController(req=request).get(tp="rbg")
        case _:
            raise HTTPException(status_code=400, detail="Endpoint inválido")
