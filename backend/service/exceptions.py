class CouldNotFetchError(Exception):
    ...


class CouldNotExecuteError(Exception):
    ...


class NetworkError(Exception):
    detail: str
    formatted_traceback: str

    def __init__(self, detail: str, traceback: str = "") -> None:
        self.detail = detail
        self.formatted_traceback = traceback
        super().__init__(detail)


class StatusCodeError(Exception):
    detail: str
    extra_data: dict | None

    def __init__(self, detail: str, extra_data: dict | None = None) -> None:
        self.detail = detail
        self.extra_data = extra_data
        super().__init__(detail)
