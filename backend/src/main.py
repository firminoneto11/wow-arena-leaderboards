from fastapi import FastAPI

from middleware import cors_middleware_config
from apps import brackets_router
from database import engine, database, create_default_data


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
    await database.connect()
    await create_default_data()


@api.on_event("shutdown")
async def shutdown() -> None:
    await database.disconnect()
