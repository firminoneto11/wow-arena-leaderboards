from models.brackets import Brackets, BracketsEnum
from typing import List


class BracketsService:

    @staticmethod
    async def create_bracket(bracket_type: str) -> Brackets:
        return await Brackets.objects.create(type=bracket_type)

    @staticmethod
    async def all_brackets() -> List[Brackets]:
        return await Brackets.objects.all()
