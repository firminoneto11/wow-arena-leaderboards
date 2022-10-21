from ormar import ReferentialAction as actions
import ormar as models

from .base import BaseModel

from .sessions import Sessions
from .wow_classes import WowClasses
from .wow_specs import WowSpecs


class PvpData(BaseModel):
    class Meta:
        tablename = "pvp_data"

    # Required Fields
    blizzard_id: int = models.BigInteger()
    name: str = models.String(max_length=50)
    global_rank: int = models.Integer()
    cr: int = models.Integer()
    played: int = models.Integer()
    wins: int = models.Integer()
    losses: int = models.Integer()
    faction_name: str = models.String(max_length=50)
    realm: str = models.String(max_length=50)
    bracket: str = models.String(max_length=10)

    # FK's - Required
    session: Sessions = models.ForeignKey(to=Sessions, ondelete=actions.CASCADE)

    # Optional Fields
    avatar_icon: str | None = models.Text(nullable=True)

    # Fk's - Optionals
    wow_class: WowClasses | None = models.ForeignKey(to=WowClasses, nullable=True, ondelete=actions.SET_NULL)
    wow_spec: WowSpecs | None = models.ForeignKey(to=WowSpecs, nullable=True, ondelete=actions.SET_NULL)
