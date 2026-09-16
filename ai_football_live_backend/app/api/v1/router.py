from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.matches import router as matches_router
from app.api.v1.leagues import router as leagues_router
from app.api.v1.ai import router as ai_router
from app.api.v1.streams import router as streams_router

router = APIRouter(prefix="/api/v1")

router.include_router(health_router)
router.include_router(matches_router)
router.include_router(leagues_router)
router.include_router(ai_router)
router.include_router(streams_router)
