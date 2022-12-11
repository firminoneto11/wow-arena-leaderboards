from fastapi import FastAPI

from api.apps.core.views import router as core_router
from ..middleware import cors_middleware_config
from conf import settings


async def startup() -> None:
    ...


async def shutdown() -> None:
    ...


def get_asgi_application() -> FastAPI:

    # Instantiating the FastAPI
    app = FastAPI(debug=settings.ENV.debug, title="Arena LeaderBoards API")

    # Adding CORS middleware to it
    app.add_middleware(**cors_middleware_config)

    # Including routers
    app.include_router(router=core_router)

    app.on_event("startup")(startup)
    app.on_event("shutdown")(shutdown)

    return app
