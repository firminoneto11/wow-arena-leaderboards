from datetime import datetime

import orm as models


def get_default_fields() -> dict:
    return {
        # PK
        "id": models.BigInteger(primary_key=True),
        # With defaults
        "created_at": models.DateTime(default=datetime.now),
        "updated_at": models.DateTime(default=datetime.now),
    }