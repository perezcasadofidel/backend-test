from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings
from app.services.innovasoft_client import InnovasoftClient

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.mongo_db


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_innovasoft_client(request: Request) -> InnovasoftClient:
    return request.app.state.innovasoft_client


async def get_current_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer requerido",
        )

    token = credentials.credentials
    session = await db[settings.sesiones_collection].find_one({"token": token})
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesion no encontrada o expirada",
        )
    return session
