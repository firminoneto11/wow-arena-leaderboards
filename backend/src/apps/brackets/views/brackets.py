from fastapi import APIRouter, Request

from ..controllers import BracketsController
from ..schemas import PvpDataAPISchema


router = APIRouter(tags=["Brackets"])


@router.get(
    path="/{bracket}/",
    response_model=list[PvpDataAPISchema],
    status_code=200,
)
async def bracket(req: Request, bracket: str):
    handler = BracketsController(req=req, bracket=bracket)
    return await handler()
