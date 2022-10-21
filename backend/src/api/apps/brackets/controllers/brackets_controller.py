from fastapi import Request

from ..models import PvpData, BracketsEnum
from .exceptions import InvalidBracketError
from ..schemas import PvpDataAPISchema


class BracketsController:

    req: Request
    bracket: str
    valid_brackets: list[str] = BracketsEnum.list_values()

    def __init__(self, req: Request, bracket: str) -> None:
        self.req, self.bracket = req, bracket
        self.validate_bracket()

    def validate_bracket(self) -> None:
        if self.bracket not in self.valid_brackets:
            raise InvalidBracketError(
                status_code=400,
                detail=f"Invalid bracket name. Valid bracket names are: {', '.join(self.valid_brackets)}",
            )

    async def __call__(self) -> list[PvpDataAPISchema]:
        queryset: list[PvpData] = (
            await PvpData.objects.filter(bracket=self.bracket)
            .select_related("session")
            .select_related("wow_class")
            .select_related("wow_spec")
            .all()
        )

        queryset[0].asDict

        return

        return list(map(lambda element: element.to_dict(), queryset))
