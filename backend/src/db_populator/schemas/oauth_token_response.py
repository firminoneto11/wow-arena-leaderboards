from .base_schema import BaseSchema


class OAuthTokenData(BaseSchema):
    access_token: str
    token_type: str
    expires_in: int
    sub: str


class OAuthTokenResponse(BaseSchema):
    error: bool | None
    message: str | None
    status_code: int | None
    data: OAuthTokenData | None
