# app/schemas/auth.py
from pydantic import BaseModel
from app.schemas.user import UserOut


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class TokenData(BaseModel):
    """
    Schema for data contained in the JWT token.
    """
    username: str | None = None