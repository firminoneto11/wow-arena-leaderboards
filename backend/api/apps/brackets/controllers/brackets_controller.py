from fastapi import Request

from ..models import PvpData, BracketsEnum
from .exceptions import InvalidBracketError


class BracketsController:

    req: Request
    bracket: str
    valid_brackets: list[str] = BracketsEnum.list_values()

    def __init__(self, req: Request, bracket: str) -> None:
        self.req, self.bracket = req, bracket

        if self.bracket not in self.valid_brackets:
            raise InvalidBracketError(
                status_code=404,
                detail=f"Invalid bracket name. Valid bracket names are: {', '.join(self.valid_brackets)}",
            )

    async def __call__(self) -> list[PvpData]:
        return (
            await PvpData.objects.filter(bracket=self.bracket)
            .select_related(["session", "wow_class", "wow_spec"])
            .order_by("-cr")
            .all()
        )
