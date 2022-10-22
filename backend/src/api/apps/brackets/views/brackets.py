from fastapi import APIRouter, Request

from ..controllers import BracketsController
from ..models import PvpData


router = APIRouter(tags=["Brackets"])


@router.get(
    path="/{bracket}/",
    response_model=list[PvpData],
    status_code=200,
)
async def bracket(req: Request, bracket: str) -> list[PvpData]:
    handler = BracketsController(req=req, bracket=bracket)
    return await handler()
