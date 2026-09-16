from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.database.repositories.match_repo import MatchRepository, LeagueRepository
from app.services.match_service import MatchService
from app.services.ai.analysis_service import AnalysisService
from app.providers.ai.factory import create_ai_provider
from app.api.error_handlers import APIError
from app.core.enums.error_codes import ErrorCode

router = APIRouter()


@router.get("/matches/{match_id}/ai-analysis")
async def get_ai_analysis(
    match_id: int,
    type: str = Query("live", description="Analysis type: pre_match, live, post_match"),
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

    ai_provider = create_ai_provider()
    analysis_service = AnalysisService(ai_provider)
    analysis = await analysis_service.generate_analysis(match, type)

    if not analysis:
        return {
            "success": True,
            "data": {
                "available": False,
                "message": "Analysis unavailable for this match",
            },
            "meta": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        }

    return {
        "success": True,
        "data": {
            "available": True,
            "id": analysis.id,
            "match_id": analysis.match_id,
            "analysis_type": analysis.analysis_type,
            "interpretation": analysis.interpretation,
            "key_insights": analysis.key_insights,
            "reference_validation_rate": analysis.reference_validation_rate,
            "validation_label": analysis.validation_label,
            "data_references": analysis.data_references,
            "validation_result": analysis.validation_result,
            "ai_provider": analysis.ai_provider,
            "generated_at": analysis.generated_at.isoformat(),
        },
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }
