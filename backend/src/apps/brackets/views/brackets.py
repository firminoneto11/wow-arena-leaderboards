from fastapi import APIRouter, Request

from ..controllers import BracketsController


router = APIRouter(tags=["Brackets"])


@router.get("/{bracket}/")
async def handle(request: Request, bracket: str):
    handler = BracketsController(req=request, bracket=bracket)
    return await handler()
