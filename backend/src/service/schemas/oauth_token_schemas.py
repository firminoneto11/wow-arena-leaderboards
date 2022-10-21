from .base_schema import BaseSchema


class OAuthTokenData(BaseSchema):
    access_token: str
    token_type: str
    expires_in: int
    sub: str


class OAuthTokenError(BaseSchema):
    error: str
    error_description: str
