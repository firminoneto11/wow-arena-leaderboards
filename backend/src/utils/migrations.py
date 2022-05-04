from connection_layer import objects
import models


async def migrate():
    await objects.create_all()


async def reset_db():
    await objects.drop_all()
