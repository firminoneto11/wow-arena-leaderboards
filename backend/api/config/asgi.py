from fastapi import FastAPI

from ..middleware import cors_middleware_config
from ..apps import brackets_router
from database import db_engine


async def startup() -> None:
    if not db_engine.db.is_connected:
        await db_engine.db.connect()


async def shutdown() -> None:
    if db_engine.db.is_connected:
        await db_engine.db.disconnect()


def get_asgi_application() -> FastAPI:

    # Instantiating the FastAPI
    application = FastAPI()

    # Adding CORS middleware to it
    application.add_middleware(**cors_middleware_config)

    # Including routers
    application.include_router(router=brackets_router, prefix="/api")

    application.on_event("startup")(startup)
    application.on_event("shutdown")(shutdown)

    return application
