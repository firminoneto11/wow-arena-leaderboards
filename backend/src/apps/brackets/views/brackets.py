from fastapi import APIRouter

from ..controllers import DataController


router = APIRouter(tags=["Brackets"])


router.get("/data/{bracket}/")(DataController.handle)
