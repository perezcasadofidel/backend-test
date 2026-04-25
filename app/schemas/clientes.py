from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ListadoClientesRequest(BaseModel):
    identificacion: str | None = None
    nombre: str | None = None
    usuarioId: str | None = None


class ClienteCrearRequest(BaseModel):
    nombre: str = Field(min_length=1)
    apellidos: str = Field(min_length=1)
    identificacion: str = Field(min_length=1)
    celular: str = Field(min_length=1)
    otroTelefono: str = Field(min_length=1)
    direccion: str = Field(min_length=1)
    fNacimiento: datetime
    fAfiliacion: datetime
    sexo: str = Field(min_length=1)
    resennaPersonal: str | None = None
    imagen: str | None = None
    interesFK: UUID
    usuarioId: str = Field(min_length=1)


class ClienteActualizarBody(BaseModel):
    nombre: str = Field(min_length=1)
    apellidos: str = Field(min_length=1)
    identificacion: str = Field(min_length=1)
    celular: str = Field(min_length=1)
    otroTelefono: str = Field(min_length=1)
    direccion: str = Field(min_length=1)
    fNacimiento: datetime
    fAfiliacion: datetime
    sexo: str = Field(min_length=1)
    resennaPersonal: str | None = None
    imagen: str | None = None
    interesFK: UUID
    usuarioId: str = Field(min_length=1)


class UpstreamProxyResponse(BaseModel):
    status_code: int
    data: Any
