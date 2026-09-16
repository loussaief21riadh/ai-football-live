from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.database.engine import engine
from app.config import settings

router = APIRouter()


async def _check_database() -> dict:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"database": "ok"}
    except Exception:
        return {"database": "error"}


async def _check_redis() -> dict:
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.cache.REDIS_URL, socket_timeout=2)
        await client.ping()
        await client.aclose()
        return {"redis": "ok"}
    except ImportError:
        return {"redis": "skipped", "detail": "redis not installed"}
    except Exception:
        return {"redis": "error"}


@router.get("/health")
async def health_check():
    db_status = await _check_database()
    redis_status = await _check_redis()

    checks = {**db_status, **redis_status}
    healthy = all(v == "ok" or v == "skipped" for v in checks.values())

    return {
        "status": "ok" if healthy else "degraded",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
