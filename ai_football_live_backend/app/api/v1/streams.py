from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import async_session
from app.providers.stream.authorized_provider import AuthorizedStreamProvider
from app.services.stream_service import StreamService
from app.database.repositories.match_repo import MatchRepository, LeagueRepository
from app.services.match_service import MatchService
from app.api.error_handlers import APIError
from app.core.enums.error_codes import ErrorCode

router = APIRouter()


async def get_db():
    async with async_session() as session:
        yield session


@router.get("/matches/{match_id}/streams")
async def get_match_streams(
    match_id: int,
    db: AsyncSession = Depends(get_db),
):
    match_repo = MatchRepository(db)
    league_repo = LeagueRepository(db)
    match_service = MatchService(match_repo, league_repo)
    match = await match_service.get_match(match_id)

    if not match:
        raise APIError(
            code=ErrorCode.MATCH_NOT_FOUND,
            message=f"Match {match_id} not found",
        )

    stream_provider = AuthorizedStreamProvider(db)
    stream_service = StreamService(stream_provider, db)
    resolution = await stream_service.resolve(match_id)

    return {
        "success": True,
        "data": {
            "available": resolution.available,
            "stream": {
                "id": resolution.stream.id,
                "provider_name": resolution.stream.provider_name,
                "embed_url": resolution.stream.embed_url,
                "quality": resolution.stream.quality,
                "language": resolution.stream.language,
            } if resolution.stream else None,
            "message": resolution.message,
            "alternatives": resolution.alternatives,
        },
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }
