from fastapi import FastAPI
from utils import migrate, start_sub_process
from tasks import fetcher


api = FastAPI()
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


@api.get("/thres_data")
async def thres_data():
    pass


@api.get("/twos_data")
async def twos_data():
    pass


@api.get("/rbg_data")
async def rbg_data():
    pass
