from fastapi import FastAPI

from middleware import cors_middleware_config
from apps import brackets_router
from database import engine


# Instantiating the FastAPI
api = FastAPI()

# Adding CORS middleware to it
api.add_middleware(**cors_middleware_config)

# Including routers
api.include_router(brackets_router)


# Startup and shutdown event handlers


@api.on_event("startup")
async def startup() -> None:
    await engine.create_all()


@api.on_event("shutdown")
async def shutdown() -> None:
    ...
