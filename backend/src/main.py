from fastapi import FastAPI, Request, HTTPException
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
