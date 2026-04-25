from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings


@dataclass
class UpstreamResponse:
    status_code: int
    data: Any


class InnovasoftClient:
    def __init__(self, http_client: httpx.AsyncClient, settings: Settings) -> None:
        self._http_client = http_client
        self._settings = settings

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        token: str | None = None,
    ) -> UpstreamResponse:
        url = f"{self._settings.innovasoft_base_url.rstrip('/')}/{path.lstrip('/')}"
        headers: dict[str, str] = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            response = await self._http_client.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=headers,
            )
        except httpx.TimeoutException:
            return UpstreamResponse(status_code=504, data={"error": "Timeout al consumir Innovasoft"})
        except httpx.HTTPError as exc:
            return UpstreamResponse(status_code=502, data={"error": f"Error de conexion con Innovasoft: {exc}"})

        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text}

        return UpstreamResponse(status_code=response.status_code, data=payload)

    async def login(self, payload: dict[str, Any]) -> UpstreamResponse:
        return await self.request("POST", "/api/Authenticate/login", json=payload)

    async def list_clients(self, payload: dict[str, Any], token: str | None = None) -> UpstreamResponse:
        return await self.request("POST", "/api/Cliente/Listado", json=payload, token=token)

    async def create_client(self, payload: dict[str, Any], token: str | None = None) -> UpstreamResponse:
        return await self.request("POST", "/api/Cliente/Crear", json=payload, token=token)

    async def update_client(self, payload: dict[str, Any], token: str | None = None) -> UpstreamResponse:
        return await self.request("POST", "/api/Cliente/Actualizar", json=payload, token=token)

    async def get_client(self, client_id: str, token: str | None = None) -> UpstreamResponse:
        return await self.request("GET", f"/api/Cliente/Obtener/{client_id}", token=token)

    async def delete_client(self, client_id: str, token: str | None = None) -> UpstreamResponse:
        return await self.request("DELETE", f"/api/Cliente/Eliminar/{client_id}", token=token)

    async def list_interests(self, token: str | None = None) -> UpstreamResponse:
        return await self.request("GET", "/api/Intereses/Listado", token=token)
