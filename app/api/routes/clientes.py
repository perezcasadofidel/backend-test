from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_session, get_db, get_innovasoft_client, get_settings
from app.core.config import Settings
from app.schemas.clientes import (
    ClienteActualizarBody,
    ClienteCrearRequest,
    ListadoClientesRequest,
    UpstreamProxyResponse,
)
from app.services.innovasoft_client import InnovasoftClient, UpstreamResponse

router = APIRouter(prefix="/clientes", tags=["clientes"])


async def _registrar_operacion(
    *,
    db: AsyncIOMotorDatabase,
    settings: Settings,
    accion: str,
    usuario: str,
    cliente_id: str,
    resultado: int,
) -> None:
    document = {
        "accion": accion,
        "usuario": usuario,
        "cliente_id": cliente_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "resultado": resultado,
    }
    await db[settings.operaciones_collection].insert_one(document)


def _raise_on_upstream_error(upstream: UpstreamResponse, action: str) -> None:
    if upstream.status_code >= 400:
        raise HTTPException(
            status_code=upstream.status_code,
            detail={
                "message": f"Error en Innovasoft durante {action}",
                "upstream": upstream.data,
            },
        )


@router.post("/listado", response_model=UpstreamProxyResponse)
async def listado_clientes(
    payload: ListadoClientesRequest,
    session: dict[str, Any] = Depends(get_current_session),
    innovasoft: InnovasoftClient = Depends(get_innovasoft_client),
) -> UpstreamProxyResponse:
    body = payload.model_dump(exclude_none=True)
    if "usuarioId" not in body and session.get("userid"):
        body["usuarioId"] = session["userid"]

    if "usuarioId" not in body:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="usuarioId es requerido para listar clientes",
        )

    upstream = await innovasoft.list_clients(body, token=session.get("token"))
    _raise_on_upstream_error(upstream, "LISTAR")
    return UpstreamProxyResponse(status_code=upstream.status_code, data=upstream.data)


@router.get("/{cliente_id}", response_model=UpstreamProxyResponse)
async def obtener_cliente(
    cliente_id: UUID,
    session: dict[str, Any] = Depends(get_current_session),
    innovasoft: InnovasoftClient = Depends(get_innovasoft_client),
) -> UpstreamProxyResponse:
    upstream = await innovasoft.get_client(str(cliente_id), token=session.get("token"))
    _raise_on_upstream_error(upstream, "OBTENER")
    return UpstreamProxyResponse(status_code=upstream.status_code, data=upstream.data)


@router.post("", response_model=UpstreamProxyResponse, status_code=status.HTTP_201_CREATED)
async def crear_cliente(
    payload: ClienteCrearRequest,
    session: dict[str, Any] = Depends(get_current_session),
    db: AsyncIOMotorDatabase = Depends(get_db),
    settings: Settings = Depends(get_settings),
    innovasoft: InnovasoftClient = Depends(get_innovasoft_client),
) -> UpstreamProxyResponse:
    upstream = await innovasoft.create_client(
        payload.model_dump(mode="json"),
        token=session.get("token"),
    )

    cliente_id = "desconocido"
    if isinstance(upstream.data, dict):
        cliente_id = str(upstream.data.get("id") or upstream.data.get("clienteId") or cliente_id)

    await _registrar_operacion(
        db=db,
        settings=settings,
        accion="CREAR",
        usuario=str(session.get("username", "desconocido")),
        cliente_id=cliente_id,
        resultado=upstream.status_code,
    )

    _raise_on_upstream_error(upstream, "CREAR")
    return UpstreamProxyResponse(status_code=upstream.status_code, data=upstream.data)


@router.put("/{cliente_id}", response_model=UpstreamProxyResponse)
async def actualizar_cliente(
    cliente_id: UUID,
    payload: ClienteActualizarBody,
    session: dict[str, Any] = Depends(get_current_session),
    db: AsyncIOMotorDatabase = Depends(get_db),
    settings: Settings = Depends(get_settings),
    innovasoft: InnovasoftClient = Depends(get_innovasoft_client),
) -> UpstreamProxyResponse:
    update_payload = payload.model_dump(mode="json")
    update_payload["id"] = str(cliente_id)

    upstream = await innovasoft.update_client(update_payload, token=session.get("token"))

    await _registrar_operacion(
        db=db,
        settings=settings,
        accion="ACTUALIZAR",
        usuario=str(session.get("username", "desconocido")),
        cliente_id=str(cliente_id),
        resultado=upstream.status_code,
    )

    _raise_on_upstream_error(upstream, "ACTUALIZAR")
    return UpstreamProxyResponse(status_code=upstream.status_code, data=upstream.data)


@router.delete("/{cliente_id}", response_model=UpstreamProxyResponse)
async def eliminar_cliente(
    cliente_id: UUID,
    session: dict[str, Any] = Depends(get_current_session),
    db: AsyncIOMotorDatabase = Depends(get_db),
    settings: Settings = Depends(get_settings),
    innovasoft: InnovasoftClient = Depends(get_innovasoft_client),
) -> UpstreamProxyResponse:
    upstream = await innovasoft.delete_client(str(cliente_id), token=session.get("token"))

    await _registrar_operacion(
        db=db,
        settings=settings,
        accion="ELIMINAR",
        usuario=str(session.get("username", "desconocido")),
        cliente_id=str(cliente_id),
        resultado=upstream.status_code,
    )

    _raise_on_upstream_error(upstream, "ELIMINAR")
    return UpstreamProxyResponse(status_code=upstream.status_code, data=upstream.data)


@router.get("/intereses/listado", response_model=UpstreamProxyResponse)
async def listado_intereses(
    session: dict[str, Any] = Depends(get_current_session),
    innovasoft: InnovasoftClient = Depends(get_innovasoft_client),
) -> UpstreamProxyResponse:
    upstream = await innovasoft.list_interests(token=session.get("token"))
    _raise_on_upstream_error(upstream, "LISTAR INTERESES")
    return UpstreamProxyResponse(status_code=upstream.status_code, data=upstream.data)
