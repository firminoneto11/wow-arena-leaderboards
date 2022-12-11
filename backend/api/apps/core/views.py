from typing import Literal

from fastapi import APIRouter

from .enums import BracketsEnum


router = APIRouter(tags=["Core"])


@router.get(path="/{bracket}/")
async def bracket(bracket: Literal[BracketsEnum.TWOS, BracketsEnum.THREES, BracketsEnum.RBG]) -> None:
    ...
