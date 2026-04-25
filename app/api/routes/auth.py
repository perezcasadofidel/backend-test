from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_session, get_db, get_innovasoft_client, get_settings
from app.core.config import Settings
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse
from app.services.innovasoft_client import InnovasoftClient

router = APIRouter(prefix="/auth", tags=["auth"])


def _extract_token(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("token", "jwt", "accessToken", "access_token"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return None


def _extract_userid(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("userid", "userId", "id"):
            value = payload.get(key)
            if value is not None:
                return str(value)

        nested = payload.get("user")
        if isinstance(nested, dict):
            for key in ("userid", "userId", "id"):
                value = nested.get(key)
                if value is not None:
                    return str(value)
    return None


def _extract_username(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("username", "userName"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value

        nested = payload.get("user")
        if isinstance(nested, dict):
            for key in ("username", "userName"):
                value = nested.get(key)
                if isinstance(value, str) and value.strip():
                    return value
    return None


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    settings: Settings = Depends(get_settings),
    innovasoft: InnovasoftClient = Depends(get_innovasoft_client),
) -> LoginResponse:
    upstream = await innovasoft.login(payload.model_dump())
    if upstream.status_code >= 400:
        raise HTTPException(
            status_code=upstream.status_code,
            detail={"message": "Login rechazado por Innovasoft", "upstream": upstream.data},
        )

    token = _extract_token(upstream.data)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": "La API de Innovasoft no retorno token JWT",
                "upstream": upstream.data,
            },
        )

    userid = _extract_userid(upstream.data)
    username = _extract_username(upstream.data) or payload.username

    session_document = {
        "token": token,
        "userid": userid,
        "username": username,
        "login_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    await db[settings.sesiones_collection].update_one(
        {"token": token},
        {"$set": session_document},
        upsert=True,
    )

    return LoginResponse(
        token=token,
        userid=userid,
        username=username,
        upstream_response=upstream.data,
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    session: dict[str, Any] = Depends(get_current_session),
    db: AsyncIOMotorDatabase = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LogoutResponse:
    token = session["token"]
    await db[settings.sesiones_collection].delete_one({"token": token})
    return LogoutResponse(message="Sesion cerrada correctamente")
