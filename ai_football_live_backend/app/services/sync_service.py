import asyncio
import logging
from datetime import datetime, timezone

from app.database.engine import async_session
from app.database.repositories.match_repo import MatchRepository, LeagueRepository, TeamRepository
from app.providers.football_data.base import FootballDataProvider
from app.config import settings

logger = logging.getLogger(__name__)


class DataSyncService:
    """Synchronizes football data from the provider into the database.

    Runs as a background task with configurable intervals.
    Handles errors gracefully without crashing the application.
    """

    def __init__(self, football_provider: FootballDataProvider):
        self._provider = football_provider
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._sync_loop())
        logger.info("DataSyncService started")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("DataSyncService stopped")

    async def _sync_loop(self) -> None:
        interval = settings.ai.AI_TIMEOUT_SECONDS  # reuse for now, or use a dedicated setting
        # Use a sensible default if not configured
        sync_interval = 30

        while self._running:
            try:
                await self._sync_once()
            except Exception as e:
                logger.error(f"Sync error: {e}")

            await asyncio.sleep(sync_interval)

    async def _sync_once(self) -> None:
        """Perform a single sync cycle."""
        async with async_session() as db:
            try:
                league_repo = LeagueRepository(db)
                team_repo = TeamRepository(db)
                match_repo = MatchRepository(db)

                # Sync leagues
                leagues = await self._provider.get_leagues()
                league_id_map = {}
                for league_data in leagues:
                    league = await league_repo.upsert({
                        "provider_name": "mock",
                        "external_id": league_data.id,
                        "name": league_data.name,
                        "country": league_data.country,
                        "logo_url": league_data.logo_url,
                        "season": league_data.season,
                    })
                    await db.flush()
                    league_id_map[league_data.id] = league.id

                # Sync teams (from matches)
                team_id_map = {}
                for match_data in [await self._provider.get_match_by_internal_id(i) for i in range(1, 5)]:
                    if match_data is None:
                        continue
                    for team in [match_data.home_team, match_data.away_team]:
                        key = (team.provider_name, team.external_id)
                        if key not in team_id_map:
                            db_team = await team_repo.upsert({
                                "provider_name": team.provider_name,
                                "external_id": team.external_id,
                                "name": team.name,
                                "short_name": team.short_name,
                                "logo_url": team.logo_url,
                            })
                            await db.flush()
                            team_id_map[key] = db_team.id

                # Sync live matches
                live_matches = await self._provider.get_live_matches()
                for match in live_matches:
                    home_key = (match.home_team.provider_name, match.home_team.external_id)
                    away_key = (match.away_team.provider_name, match.away_team.external_id)

                    home_team_db = await team_repo.upsert({
                        "provider_name": match.home_team.provider_name,
                        "external_id": match.home_team.external_id,
                        "name": match.home_team.name,
                        "short_name": match.home_team.short_name,
                        "logo_url": match.home_team.logo_url,
                    })
                    away_team_db = await team_repo.upsert({
                        "provider_name": match.away_team.provider_name,
                        "external_id": match.away_team.external_id,
                        "name": match.away_team.name,
                        "short_name": match.away_team.short_name,
                        "logo_url": match.away_team.logo_url,
                    })
                    await db.flush()

                    league_key = (match.league.provider_name, match.league.external_id)
                    league_db = await league_repo.upsert({
                        "provider_name": match.league.provider_name,
                        "external_id": match.league.external_id,
                        "name": match.league.name,
                        "country": match.league.country,
                        "logo_url": match.league.logo_url,
                        "season": match.league.season,
                    })
                    await db.flush()

                    await match_repo.upsert({
                        "provider_name": match.provider_name,
                        "external_id": match.external_id,
                        "league_id": league_db.id,
                        "home_team_id": home_team_db.id,
                        "away_team_id": away_team_db.id,
                        "status": match.status.value,
                        "minute": match.minute,
                        "added_time": match.added_time,
                        "home_score": match.home_score,
                        "away_score": match.away_score,
                        "ht_home_score": match.ht_home_score,
                        "ht_away_score": match.ht_away_score,
                        "match_date": match.match_date,
                        "venue": match.venue,
                        "referee": match.referee,
                    })
                    await db.flush()

                await db.commit()
                logger.debug("Sync cycle completed")

            except Exception as e:
                await db.rollback()
                raise e
