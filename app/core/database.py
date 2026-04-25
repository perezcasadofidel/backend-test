from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING

from app.core.config import Settings


class MongoManager:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncIOMotorClient | None = None
        self._database: AsyncIOMotorDatabase | None = None

    async def connect(self) -> AsyncIOMotorDatabase:
        self._client = AsyncIOMotorClient(self._settings.mongodb_uri)
        self._database = self._client[self._settings.mongodb_database]
        await self._ensure_indexes()
        return self._database

    async def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()

    @property
    def database(self) -> AsyncIOMotorDatabase:
        if self._database is None:
            raise RuntimeError("MongoDB no esta inicializado")
        return self._database

    async def _ensure_indexes(self) -> None:
        if self._database is None:
            return

        sesiones = self._database[self._settings.sesiones_collection]
        operaciones = self._database[self._settings.operaciones_collection]

        await sesiones.create_index([("token", ASCENDING)], unique=True)
        await sesiones.create_index([("username", ASCENDING)])
        await operaciones.create_index([("timestamp", ASCENDING)])
        await operaciones.create_index([("usuario", ASCENDING), ("accion", ASCENDING)])
