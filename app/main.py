from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, clientes, health
from app.core.config import get_settings
from app.core.database import MongoManager
from app.services.innovasoft_client import InnovasoftClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    mongo_manager = MongoManager(settings)
    mongo_db = await mongo_manager.connect()

    timeout = httpx.Timeout(settings.innovasoft_timeout_seconds)
    http_client = httpx.AsyncClient(timeout=timeout)
    innovasoft_client = InnovasoftClient(http_client=http_client, settings=settings)

    app.state.settings = settings
    app.state.mongo_manager = mongo_manager
    app.state.mongo_db = mongo_db
    app.state.http_client = http_client
    app.state.innovasoft_client = innovasoft_client

    try:
        yield
    finally:
        await http_client.aclose()
        await mongo_manager.disconnect()


settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(clientes.router, prefix=settings.api_prefix)
