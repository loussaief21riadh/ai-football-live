from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import async_session
from app.services.match_service import MatchService
from app.database.repositories.match_repo import MatchRepository, LeagueRepository
from app.api.error_handlers import APIError
from app.core.enums.error_codes import ErrorCode

router = APIRouter()


async def get_db():
    async with async_session() as session:
        yield session


def _match_to_dict(match) -> dict[str, Any]:
    return {
        "id": match.id,
        "provider_name": match.provider_name,
        "external_id": match.external_id,
        "league": {
            "id": match.league.id,
            "provider_name": match.league.provider_name,
            "external_id": match.league.external_id,
            "name": match.league.name,
            "country": match.league.country,
            "logo_url": match.league.logo_url,
            "season": match.league.season,
        },
        "home_team": {
            "id": match.home_team.id,
            "provider_name": match.home_team.provider_name,
            "external_id": match.home_team.external_id,
            "name": match.home_team.name,
            "short_name": match.home_team.short_name,
            "logo_url": match.home_team.logo_url,
        },
        "away_team": {
            "id": match.away_team.id,
            "provider_name": match.away_team.provider_name,
            "external_id": match.away_team.external_id,
            "name": match.away_team.name,
            "short_name": match.away_team.short_name,
            "logo_url": match.away_team.logo_url,
        },
        "status": match.status.value,
        "minute": match.minute,
        "added_time": match.added_time,
        "home_score": match.home_score,
        "away_score": match.away_score,
        "ht_home_score": match.ht_home_score,
        "ht_away_score": match.ht_away_score,
        "match_date": match.match_date.isoformat(),
        "venue": match.venue,
        "referee": match.referee,
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type.value,
                "minute": e.minute,
                "added_time": e.added_time,
                "player_name": e.player_name,
                "assist_player": e.assist_player,
                "team_id": e.team_id,
                "detail": e.detail,
            }
            for e in match.events
        ],
        "statistics": [
            {
                "id": s.id,
                "stat_type": s.stat_type,
                "home_value": s.home_value,
                "away_value": s.away_value,
            }
            for s in match.statistics
        ],
        "created_at": match.created_at.isoformat(),
        "updated_at": match.updated_at.isoformat(),
    }


@router.get("/matches")
async def get_matches(
    status: str | None = Query(None, description="Filter by status"),
    league_id: int | None = Query(None, description="Filter by league ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    match_repo = MatchRepository(db)
    league_repo = LeagueRepository(db)
    service = MatchService(match_repo, league_repo)
    matches = await service.get_matches(status=status, league_id=league_id, limit=limit, offset=offset)
    total = await service.count_matches(status=status)
    return {
        "success": True,
        "data": [_match_to_dict(m) for m in matches],
        "meta": {
            "page": offset // limit + 1,
            "limit": limit,
            "total": total,
            "cached": False,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


@router.get("/matches/live")
async def get_live_matches(
    db: AsyncSession = Depends(get_db),
):
    match_repo = MatchRepository(db)
    league_repo = LeagueRepository(db)
    service = MatchService(match_repo, league_repo)
    matches = await service.get_live_matches()
    return {
        "success": True,
        "data": [_match_to_dict(m) for m in matches],
        "meta": {
            "total": len(matches),
            "cached": False,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


@router.get("/matches/{match_id}")
async def get_match(
    match_id: int,
    db: AsyncSession = Depends(get_db),
):
    match_repo = MatchRepository(db)
    league_repo = LeagueRepository(db)
    service = MatchService(match_repo, league_repo)
    match = await service.get_match(match_id)
    if not match:
        raise APIError(
            code=ErrorCode.MATCH_NOT_FOUND,
            message=f"Match {match_id} not found",
        )
    return {
        "success": True,
        "data": _match_to_dict(match),
        "meta": {
            "cached": False,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }
