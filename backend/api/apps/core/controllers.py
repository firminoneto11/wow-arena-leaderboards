from typing import Literal

from .enums import BracketsEnum


async def bracket_controller(bracket: Literal[BracketsEnum.TWOS, BracketsEnum.THREES, BracketsEnum.RBG]) -> None:
    ...
