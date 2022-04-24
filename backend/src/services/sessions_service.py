from models.sessions import Sessions
from typing import List


class SessionsService:
    
    @staticmethod
    async def create_session(session: int) -> Sessions:
        return await Sessions.objects.create(type=session)

    @staticmethod
    async def all_sessions() -> List[Sessions]:
        return await Sessions.objects.all()
