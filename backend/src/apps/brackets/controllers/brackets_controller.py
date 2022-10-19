from fastapi import Request


class BracketsController:

    req: Request
    bracket: str

    def __init__(self, req: Request, bracket: str) -> None:
        self.req = req
        self.bracket = bracket

    async def __call__(self) -> None:
        pass
