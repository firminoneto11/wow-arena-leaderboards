from fastapi import FastAPI

from apps.brackets.views import brackets_router
from database import db_engine
from middleware import cors_middleware_config

# Instantiating the FastAPI
api = FastAPI()

# Adding CORS middleware to it
api.add_middleware(**cors_middleware_config)

# Including routers
api.include_router(brackets_router)


# Startup and shutdown event handlers


@api.on_event("startup")
async def startup() -> None:
    await db_engine.create_all()


@api.on_event("shutdown")
async def shutdown() -> None:
    ...
