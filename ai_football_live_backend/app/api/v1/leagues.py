from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.database.repositories.match_repo import LeagueRepository
from app.services.match_service import MatchService

router = APIRouter()


@router.get("/leagues")
async def get_leagues(
    db: AsyncSession = Depends(get_db),
):
    league_repo = LeagueRepository(db)
    leagues = await league_repo.find_all()
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
