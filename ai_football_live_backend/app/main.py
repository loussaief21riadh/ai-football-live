import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import router as v1_router
from app.api.error_handlers import APIError, api_error_handler, generic_error_handler
from app.services.sync_service import DataSyncService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    from app.providers.football.factory import create_football_provider

    football_provider = create_football_provider()
    sync_service = DataSyncService(football_provider)
    await sync_service.start()

    yield

    await sync_service.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Football Live",
        description="AI Football Live - Backend API",
        version="0.1.0",
        lifespan=lifespan,
    )

    cors_origins = settings.cors.CORS_ORIGINS
    if cors_origins == "*":
        allow_origins = ["*"]
    else:
        allow_origins = [o.strip() for o in cors_origins.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_origins != ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    app.include_router(v1_router)

    return app


app = create_app()
