import json
from datetime import datetime, timezone

from app.database.repositories.match_repo import MatchRepository, LeagueRepository
from app.database.models import MatchModel, LeagueModel
from app.core.domain.match import Match, League, Team, MatchEvent, MatchStatistic
from app.core.enums.match_status import MatchStatus, EventType


class MatchService:
    def __init__(self, match_repo: MatchRepository, league_repo: LeagueRepository):
        self._match_repo = match_repo
        self._league_repo = league_repo

    async def get_matches(
        self,
        status: str | None = None,
        league_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Match]:
        models = await self._match_repo.find_all(status=status, league_id=league_id, limit=limit, offset=offset)
        return [self._to_domain(m) for m in models]

    async def get_live_matches(self) -> list[Match]:
        models = await self._match_repo.find_live()
        return [self._to_domain(m) for m in models]

    async def get_match(self, match_id: int) -> Match | None:
        model = await self._match_repo.find_by_id(match_id)
        if not model:
            return None
        return self._to_domain(model)

    async def get_leagues(self) -> list[League]:
        models = await self._league_repo.find_all()
        return [self._league_to_domain(m) for m in models]

    async def count_matches(self, status: str | None = None) -> int:
        return await self._match_repo.count(status=status)

    def _to_domain(self, model: MatchModel) -> Match:
        try:
            events = [self._event_to_domain(e) for e in (model.events or [])]
        except Exception:
            events = []
        try:
            statistics = [self._stat_to_domain(s) for s in (model.statistics or [])]
        except Exception:
            statistics = []

        return Match(
            id=model.id,
            provider_name=model.provider_name,
            external_id=model.external_id,
            league=self._league_to_domain(model.league),
            home_team=self._team_to_domain(model.home_team),
            away_team=self._team_to_domain(model.away_team),
            status=MatchStatus.from_str(model.status),
            match_date=model.match_date,
            venue=model.venue,
            referee=model.referee,
            minute=model.minute,
            added_time=model.added_time,
            home_score=model.home_score or 0,
            away_score=model.away_score or 0,
            ht_home_score=model.ht_home_score,
            ht_away_score=model.ht_away_score,
            events=events,
            statistics=statistics,
            created_at=model.created_at or datetime.now(timezone.utc),
            updated_at=model.updated_at or datetime.now(timezone.utc),
        )

    def _league_to_domain(self, model: LeagueModel) -> League:
        return League(
            id=model.id,
            provider_name=model.provider_name,
            external_id=model.external_id,
            name=model.name,
            country=model.country,
            logo_url=model.logo_url,
            season=model.season,
        )

    def _team_to_domain(self, model) -> Team:
        return Team(
            id=model.id,
            provider_name=model.provider_name,
            external_id=model.external_id,
            name=model.name,
            short_name=model.short_name,
            logo_url=model.logo_url,
        )

    def _event_to_domain(self, model) -> MatchEvent:
        return MatchEvent(
            id=model.id,
            match_id=model.match_id,
            provider_name=model.provider_name,
            external_event_id=model.external_event_id,
            event_type=EventType.from_str(model.event_type),
            minute=model.minute,
            added_time=model.added_time,
            team_id=model.team_id,
            player_name=model.player_name,
            assist_player=model.assist_player,
            detail=model.detail,
        )

    def _stat_to_domain(self, model) -> MatchStatistic:
        return MatchStatistic(
            id=model.id,
            match_id=model.match_id,
            stat_type=model.stat_type,
            home_value=model.home_value,
            away_value=model.away_value,
        )
