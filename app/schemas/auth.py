from typing import Any

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    token: str
    userid: str | None = None
    username: str
    upstream_response: Any


class LogoutResponse(BaseModel):
    message: str
