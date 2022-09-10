from database.connection_layer import objects
import models


async def migrate():
    await objects.create_all()
    await models.Brackets.objects.get_or_create(type="2v2", defaults={"type": "2v2"})
    await models.Brackets.objects.get_or_create(type="3v3", defaults={"type": "3v3"})
    await models.Brackets.objects.get_or_create(type="rbg", defaults={"type": "rbg"})


async def reset_db():
    await objects.drop_all()
