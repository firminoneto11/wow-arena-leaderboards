from datetime import datetime

import ormar as models

from database import db_engine


class BaseModel(models.Model):
    class Meta:
        abstract = True
        metadata = db_engine.metadata
        database = db_engine.db

    id: int = models.BigInteger(primary_key=True)
    created_at: datetime = models.DateTime(default=datetime.now)
    updated_at: datetime = models.DateTime(default=datetime.now)
