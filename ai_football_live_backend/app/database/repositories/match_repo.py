from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import MatchModel, LeagueModel, TeamModel
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
        from sqlalchemy import func

        query = select(func.count()).select_from(MatchModel)
        if status and status != "all":
            query = query.where(MatchModel.status == status)
        result = await self._db.execute(query)
        return result.scalar() or 0


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
