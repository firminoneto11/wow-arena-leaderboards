from fastapi import APIRouter, Request

from .controllers import BracketsController
from .schemas import BracketsResponseSchema


router = APIRouter(tags=["Brackets"])


@router.get(
    path="/{bracket}/",
    response_model=list[BracketsResponseSchema],
    status_code=200,
)
async def bracket(req: Request, bracket: str) -> list[BracketsResponseSchema]:
    handler = BracketsController(req=req, bracket=bracket)
    return await handler()
