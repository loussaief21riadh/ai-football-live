from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import (
    MatchModel, LeagueModel, TeamModel,
    MatchEventModel, MatchStatisticModel,
)
from app.core.enums.match_status import MatchStatus


class MatchRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def find_all(
        self,
        status: str | None = None,
        league_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MatchModel]:
        query = select(MatchModel).options(
            selectinload(MatchModel.league),
            selectinload(MatchModel.home_team),
            selectinload(MatchModel.away_team),
        )

        if status and status != "all":
            query = query.where(MatchModel.status == status)
        if league_id:
            query = query.where(MatchModel.league_id == league_id)

        query = query.order_by(MatchModel.match_date.desc())
        query = query.offset(offset).limit(limit)

        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def find_live(self) -> list[MatchModel]:
        query = (
            select(MatchModel)
            .options(
                selectinload(MatchModel.league),
                selectinload(MatchModel.home_team),
                selectinload(MatchModel.away_team),
            )
            .where(MatchModel.status.in_(["live", "halftime"]))
            .order_by(MatchModel.match_date.desc())
        )
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def find_by_id(self, match_id: int) -> MatchModel | None:
        query = (
            select(MatchModel)
            .options(
                selectinload(MatchModel.league),
                selectinload(MatchModel.home_team),
                selectinload(MatchModel.away_team),
                selectinload(MatchModel.events),
                selectinload(MatchModel.statistics),
            )
            .where(MatchModel.id == match_id)
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def count(self, status: str | None = None) -> int:
        query = select(func.count()).select_from(MatchModel)
        if status and status != "all":
            query = query.where(MatchModel.status == status)
        result = await self._db.execute(query)
        return result.scalar() or 0

    async def upsert(self, match_data: dict) -> MatchModel:
        """Insert or update a match by provider_name + external_id."""
        provider_name = match_data["provider_name"]
        external_id = match_data["external_id"]

        query = select(MatchModel).where(
            MatchModel.provider_name == provider_name,
            MatchModel.external_id == external_id,
        )
        result = await self._db.execute(query)
        existing = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if existing:
            for key, value in match_data.items():
                if key not in ("provider_name", "external_id") and value is not None:
                    setattr(existing, key, value)
            existing.updated_at = now
            await self._db.flush()
            return existing
        else:
            match = MatchModel(
                provider_name=provider_name,
                external_id=external_id,
                league_id=match_data.get("league_id"),
                home_team_id=match_data.get("home_team_id"),
                away_team_id=match_data.get("away_team_id"),
                status=match_data.get("status", "scheduled"),
                minute=match_data.get("minute"),
                added_time=match_data.get("added_time"),
                home_score=match_data.get("home_score", 0),
                away_score=match_data.get("away_score", 0),
                ht_home_score=match_data.get("ht_home_score"),
                ht_away_score=match_data.get("ht_away_score"),
                match_date=match_data.get("match_date", now),
                venue=match_data.get("venue"),
                referee=match_data.get("referee"),
                created_at=now,
                updated_at=now,
            )
            self._db.add(match)
            await self._db.flush()
            return match

    async def upsert_events(self, match_id: int, events: list[dict]) -> None:
        """Replace all events for a match."""
        from sqlalchemy import delete

        await self._db.execute(
            delete(MatchEventModel).where(MatchEventModel.match_id == match_id)
        )

        for event_data in events:
            event = MatchEventModel(
                match_id=match_id,
                provider_name=event_data.get("provider_name", "api_football"),
                external_event_id=event_data.get("external_event_id"),
                event_type=event_data.get("event_type", "unknown"),
                minute=event_data.get("minute", 0),
                added_time=event_data.get("added_time"),
                team_id=event_data.get("team_id"),
                player_name=event_data.get("player_name"),
                assist_player=event_data.get("assist_player"),
                detail=event_data.get("detail"),
            )
            self._db.add(event)

        await self._db.flush()

    async def upsert_statistics(self, match_id: int, stats: list[dict]) -> None:
        """Replace all statistics for a match."""
        from sqlalchemy import delete

        await self._db.execute(
            delete(MatchStatisticModel).where(MatchStatisticModel.match_id == match_id)
        )

        for stat_data in stats:
            stat = MatchStatisticModel(
                match_id=match_id,
                stat_type=stat_data.get("stat_type", "unknown"),
                home_value=stat_data.get("home_value"),
                away_value=stat_data.get("away_value"),
            )
            self._db.add(stat)

        await self._db.flush()


class LeagueRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def find_all(self) -> list[LeagueModel]:
        query = select(LeagueModel).order_by(LeagueModel.name)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def find_by_id(self, league_id: int) -> LeagueModel | None:
        query = select(LeagueModel).where(LeagueModel.id == league_id)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def upsert(self, league_data: dict) -> LeagueModel:
        """Insert or update a league by provider_name + external_id."""
        provider_name = league_data["provider_name"]
        external_id = league_data["external_id"]

        query = select(LeagueModel).where(
            LeagueModel.provider_name == provider_name,
            LeagueModel.external_id == external_id,
        )
        result = await self._db.execute(query)
        existing = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if existing:
            for key, value in league_data.items():
                if key not in ("provider_name", "external_id") and value is not None:
                    setattr(existing, key, value)
            existing.updated_at = now
            await self._db.flush()
            return existing
        else:
            league = LeagueModel(
                provider_name=provider_name,
                external_id=external_id,
                name=league_data.get("name", ""),
                country=league_data.get("country"),
                logo_url=league_data.get("logo_url"),
                season=league_data.get("season"),
                created_at=now,
                updated_at=now,
            )
            self._db.add(league)
            await self._db.flush()
            return league


class TeamRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def upsert(self, team_data: dict) -> TeamModel:
        """Insert or update a team by provider_name + external_id."""
        provider_name = team_data["provider_name"]
        external_id = team_data["external_id"]

        query = select(TeamModel).where(
            TeamModel.provider_name == provider_name,
            TeamModel.external_id == external_id,
        )
        result = await self._db.execute(query)
        existing = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if existing:
            for key, value in team_data.items():
                if key not in ("provider_name", "external_id") and value is not None:
                    setattr(existing, key, value)
            existing.updated_at = now
            await self._db.flush()
            return existing
        else:
            team = TeamModel(
                provider_name=provider_name,
                external_id=external_id,
                name=team_data.get("name", ""),
                short_name=team_data.get("short_name"),
                logo_url=team_data.get("logo_url"),
                created_at=now,
                updated_at=now,
            )
            self._db.add(team)
            await self._db.flush()
            return team
