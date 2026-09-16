import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from app.core.domain.match import Match, League, Team, MatchEvent, MatchStatistic
from app.core.enums.match_status import MatchStatus, EventType


@pytest.fixture
def api_football_match():
    """Match as returned by ApiFootballProvider — id is None, external_id is the fixture ID."""
    league = League(
        id=None, provider_name="api-football", external_id=39,
        name="Premier League", country="England",
    )
    home = Team(
        id=None, provider_name="api-football", external_id=42,
        name="Arsenal", short_name="ARS",
    )
    away = Team(
        id=None, provider_name="api-football", external_id=49,
        name="Chelsea", short_name="CHE",
    )
    return Match(
        id=None,
        provider_name="api-football",
        external_id=1585230,
        league=league,
        home_team=home,
        away_team=away,
        status=MatchStatus.LIVE,
        match_date=datetime.now(timezone.utc),
        minute=67,
        home_score=2,
        away_score=1,
    )


@pytest.fixture
def mock_provider_with_api_match(api_football_match):
    provider = AsyncMock()
    provider.get_leagues.return_value = [api_football_match.league]
    provider.get_live_matches.return_value = [api_football_match]
    provider.get_upcoming_matches.return_value = []
    provider.get_match_events.return_value = [
        MatchEvent(
            id=None, match_id=0, provider_name="api-football",
            external_event_id="evt_9001", event_type=EventType.GOAL,
            minute=23, team_id=42, player_name="Bukayo Saka",
        ),
    ]
    provider.get_match_statistics.return_value = [
        MatchStatistic(
            id=None, match_id=0, stat_type="Ball Possession",
            home_value="58%", away_value="42%",
        ),
    ]
    return provider


class TestFinding1Regression:
    """Regression tests for Finding 1: sync must use match.external_id, not match.id."""

    @pytest.mark.asyncio
    async def test_events_called_with_external_id(self, api_football_match, mock_provider_with_api_match):
        """get_match_events must receive match.external_id, not match.id (which is None)."""
        mock_repo_instance = MagicMock()
        mock_repo_instance.id = 1

        with patch("app.services.sync_service.async_session") as mock_session_ctx:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session_ctx.return_value = mock_session

            with patch("app.services.sync_service.LeagueRepository") as MockLeagueRepo:
                with patch("app.services.sync_service.TeamRepository") as MockTeamRepo:
                    with patch("app.services.sync_service.MatchRepository") as MockMatchRepo:
                        MockLeagueRepo.return_value = MagicMock(upsert=AsyncMock(return_value=mock_repo_instance))
                        MockTeamRepo.return_value = MagicMock(upsert=AsyncMock(return_value=mock_repo_instance))
                        mock_match_repo = MagicMock()
                        mock_match_repo.upsert = AsyncMock(return_value=mock_repo_instance)
                        mock_match_repo.upsert_events = AsyncMock()
                        mock_match_repo.upsert_statistics = AsyncMock()
                        MockMatchRepo.return_value = mock_match_repo

                        from app.services.sync_service import DataSyncService
                        service = DataSyncService(mock_provider_with_api_match)
                        await service._sync_once()

                        mock_provider_with_api_match.get_match_events.assert_called_once()
                        call_args = mock_provider_with_api_match.get_match_events.call_args
                        assert call_args[0][0] == 1585230, (
                            f"get_match_events received {call_args[0][0]}, "
                            f"expected external_id=1585230, not match.id=None"
                        )

    @pytest.mark.asyncio
    async def test_statistics_called_with_external_id(self, api_football_match, mock_provider_with_api_match):
        """get_match_statistics must receive match.external_id, not match.id (which is None)."""
        mock_repo_instance = MagicMock()
        mock_repo_instance.id = 1

        with patch("app.services.sync_service.async_session") as mock_session_ctx:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session_ctx.return_value = mock_session

            with patch("app.services.sync_service.LeagueRepository") as MockLeagueRepo:
                with patch("app.services.sync_service.TeamRepository") as MockTeamRepo:
                    with patch("app.services.sync_service.MatchRepository") as MockMatchRepo:
                        MockLeagueRepo.return_value = MagicMock(upsert=AsyncMock(return_value=mock_repo_instance))
                        MockTeamRepo.return_value = MagicMock(upsert=AsyncMock(return_value=mock_repo_instance))
                        mock_match_repo = MagicMock()
                        mock_match_repo.upsert = AsyncMock(return_value=mock_repo_instance)
                        mock_match_repo.upsert_events = AsyncMock()
                        mock_match_repo.upsert_statistics = AsyncMock()
                        MockMatchRepo.return_value = mock_match_repo

                        from app.services.sync_service import DataSyncService
                        service = DataSyncService(mock_provider_with_api_match)
                        await service._sync_once()

                        mock_provider_with_api_match.get_match_statistics.assert_called_once()
                        call_args = mock_provider_with_api_match.get_match_statistics.call_args
                        assert call_args[0][0] == 1585230, (
                            f"get_match_statistics received {call_args[0][0]}, "
                            f"expected external_id=1585230, not match.id=None"
                        )

    @pytest.mark.asyncio
    async def test_match_id_not_used_for_api_calls(self, api_football_match, mock_provider_with_api_match):
        """Verify that match.id (None) is never passed to provider event/stat methods."""
        mock_repo_instance = MagicMock()
        mock_repo_instance.id = 1

        with patch("app.services.sync_service.async_session") as mock_session_ctx:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session_ctx.return_value = mock_session

            with patch("app.services.sync_service.LeagueRepository") as MockLeagueRepo:
                with patch("app.services.sync_service.TeamRepository") as MockTeamRepo:
                    with patch("app.services.sync_service.MatchRepository") as MockMatchRepo:
                        MockLeagueRepo.return_value = MagicMock(upsert=AsyncMock(return_value=mock_repo_instance))
                        MockTeamRepo.return_value = MagicMock(upsert=AsyncMock(return_value=mock_repo_instance))
                        mock_match_repo = MagicMock()
                        mock_match_repo.upsert = AsyncMock(return_value=mock_repo_instance)
                        mock_match_repo.upsert_events = AsyncMock()
                        mock_match_repo.upsert_statistics = AsyncMock()
                        MockMatchRepo.return_value = mock_match_repo

                        from app.services.sync_service import DataSyncService
                        service = DataSyncService(mock_provider_with_api_match)
                        await service._sync_once()

                        for call in mock_provider_with_api_match.get_match_events.call_args_list:
                            assert call[0][0] is not None, "get_match_events received None"
                        for call in mock_provider_with_api_match.get_match_statistics.call_args_list:
                            assert call[0][0] is not None, "get_match_statistics received None"

    @pytest.mark.asyncio
    async def test_sync_idempotency_unchanged(self, mock_provider_with_api_match):
        """Existing sync idempotency behavior remains unchanged after Finding 1 fix."""
        mock_repo_instance = MagicMock()
        mock_repo_instance.id = 1

        with patch("app.services.sync_service.async_session") as mock_session_ctx:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session_ctx.return_value = mock_session

            with patch("app.services.sync_service.LeagueRepository") as MockLeagueRepo:
                with patch("app.services.sync_service.TeamRepository") as MockTeamRepo:
                    with patch("app.services.sync_service.MatchRepository") as MockMatchRepo:
                        MockLeagueRepo.return_value = MagicMock(upsert=AsyncMock(return_value=mock_repo_instance))
                        MockTeamRepo.return_value = MagicMock(upsert=AsyncMock(return_value=mock_repo_instance))
                        mock_match_repo = MagicMock()
                        mock_match_repo.upsert = AsyncMock(return_value=mock_repo_instance)
                        mock_match_repo.upsert_events = AsyncMock()
                        mock_match_repo.upsert_statistics = AsyncMock()
                        MockMatchRepo.return_value = mock_match_repo

                        from app.services.sync_service import DataSyncService
                        service = DataSyncService(mock_provider_with_api_match)
                        await service._sync_once()

                        mock_provider_with_api_match.get_live_matches.assert_called_once()
                        mock_provider_with_api_match.get_upcoming_matches.assert_called_once_with(hours=24)
                        mock_match_repo.upsert.assert_called_once()
                        mock_match_repo.upsert_events.assert_called_once()
                        mock_match_repo.upsert_statistics.assert_called_once()
