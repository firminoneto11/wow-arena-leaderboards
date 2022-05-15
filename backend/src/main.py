from fastapi import FastAPI, Request
from utils import migrate, start_sub_process
from tasks import fetcher
from schemas import WowDataSchema
from controllers import DataController
from middlewares import cors_middleware_config


api = FastAPI()
api.add_middleware(**cors_middleware_config)

sub_process = None


@api.on_event("startup")
async def startup():
    # global sub_process
    # await migrate()
    # await fetcher()
    # sub_process = start_sub_process(task=hello_world)  # TODO: Trocar o argumento para a função 'fetcher'
    pass


@api.on_event("shutdown")
async def shutdown():
    global sub_process
    if sub_process is not None:
        try:
            sub_process.terminate()
        except Exception as e:
            print(f"Error while terminating the sub process: {e}")


@api.get("/threes_data/", response_model=WowDataSchema)
async def threes_data(request: Request):
    return await DataController(req=request).get(tp="3v3")


@api.get("/twos_data/", response_model=WowDataSchema)
async def twos_data(request: Request):
    return await DataController(req=request).get(tp="2v2")


@api.get("/rbg_data/", response_model=WowDataSchema)
async def rbg_data(request: Request):
    return await DataController(req=request).get(tp="rbg")
