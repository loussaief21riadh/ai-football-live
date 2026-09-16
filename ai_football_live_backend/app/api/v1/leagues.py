from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import async_session
from app.database.repositories.match_repo import LeagueRepository
from app.services.match_service import MatchService

router = APIRouter()


async def get_db():
    async with async_session() as session:
        yield session


@router.get("/leagues")
async def get_leagues(
    db: AsyncSession = Depends(get_db),
):
    match_repo = type("MockMatchRepo", (), {"find_all": lambda self, **kw: [], "find_live": lambda self: [], "count": lambda self, **kw: 0})()
    league_repo = LeagueRepository(db)
    service = MatchService(match_repo, league_repo)
    leagues = await service.get_leagues()
    return {
        "success": True,
        "data": [
            {
                "id": l.id,
                "provider_name": l.provider_name,
                "external_id": l.external_id,
                "name": l.name,
                "country": l.country,
                "logo_url": l.logo_url,
                "season": l.season,
            }
            for l in leagues
        ],
        "meta": {
            "total": len(leagues),
            "cached": False,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }
