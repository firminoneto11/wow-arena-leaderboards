from fastapi import APIRouter

from .controllers import bracket_controller


router = APIRouter(tags=["Core"])


router.add_api_route(path="/{bracket}/", endpoint=bracket_controller, status_code=200)
