from connection_layer import objects
import models


async def migrate():
    await objects.create_all()
