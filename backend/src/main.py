from fastapi import FastAPI

from apps import brackets_router
from middleware import cors_middleware_config
from database import db_engine


# Instantiating the FastAPI
app = FastAPI()

# Adding CORS middleware to it
app.add_middleware(**cors_middleware_config)

# Including routers
app.include_router(router=brackets_router, prefix="/api")


# Startup and shutdown event handlers


@app.on_event("startup")
async def startup() -> None:
    await db_engine.create_all()

    if not db_engine.db.is_connected:
        await db_engine.db.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    if db_engine.db.is_connected:
        await db_engine.db.disconnect()
