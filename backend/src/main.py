from fastapi import FastAPI

from apps.brackets.views import brackets_router
from middlewares import cors_middleware_config
from connection_layer import *


# Instantiating the FastAPI
api = FastAPI()

# Adding CORS middleware to it
api.add_middleware(**cors_middleware_config)

# Including routers
api.include_router(brackets_router)


# Startup and shutdown event handlers


@api.on_event("startup")
async def startup() -> None:
    ...


@api.on_event("shutdown")
async def shutdown() -> None:
    ...
