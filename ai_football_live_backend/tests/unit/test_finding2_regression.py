import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from app.core.domain.match import Match, League, Team, MatchEvent, MatchStatistic
from app.core.enums.match_status import MatchStatus, EventType


def _make_match(status: MatchStatus, external_id: int = 1585230) -> Match:
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
        external_id=external_id,
        league=league,
        home_team=home,
        away_team=away,
        status=status,
        match_date=datetime.now(timezone.utc),
        minute=67 if status in (MatchStatus.LIVE, MatchStatus.HALFTIME) else None,
        home_score=2 if status not in (MatchStatus.SCHEDULED,) else None,
        away_score=1 if status not in (MatchStatus.SCHEDULED,) else None,
    )


def _make_provider(matches: list[Match]) -> AsyncMock:
    provider = AsyncMock()
    provider.get_leagues.return_value = [matches[0].league] if matches else []
    provider.get_live_matches.return_value = [
        m for m in matches if m.status in (MatchStatus.LIVE, MatchStatus.HALFTIME)
    ]
    provider.get_upcoming_matches.return_value = [
        m for m in matches if m.status == MatchStatus.SCHEDULED
    ]
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


async def _run_sync(provider: AsyncMock) -> MagicMock:
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
                    service = DataSyncService(provider)
                    await service._sync_once()
                    return mock_match_repo


class TestFinding2Regression:
    """Regression tests for Finding 2: events/stats should only be fetched for meaningful statuses."""

    @pytest.mark.asyncio
    async def test_events_not_fetched_for_scheduled(self):
        """get_match_events must NOT be called for SCHEDULED matches."""
        match = _make_match(MatchStatus.SCHEDULED)
        provider = _make_provider([match])
        await _run_sync(provider)
        provider.get_match_events.assert_not_called()

    @pytest.mark.asyncio
    async def test_stats_not_fetched_for_scheduled(self):
        """get_match_statistics must NOT be called for SCHEDULED matches."""
        match = _make_match(MatchStatus.SCHEDULED)
        provider = _make_provider([match])
        await _run_sync(provider)
        provider.get_match_statistics.assert_not_called()

    @pytest.mark.asyncio
    async def test_events_fetched_for_live(self):
        """get_match_events MUST be called for LIVE matches."""
        match = _make_match(MatchStatus.LIVE)
        provider = _make_provider([match])
        await _run_sync(provider)
        provider.get_match_events.assert_called_once()

    @pytest.mark.asyncio
    async def test_events_fetched_for_halftime(self):
        """get_match_events MUST be called for HALFTIME matches."""
        match = _make_match(MatchStatus.HALFTIME)
        provider = _make_provider([match])
        await _run_sync(provider)
        provider.get_match_events.assert_called_once()

    @pytest.mark.asyncio
    async def test_events_fetched_for_finished(self):
        """get_match_events MUST be called for FINISHED matches (if they enter the sync loop)."""
        match = _make_match(MatchStatus.FINISHED)
        provider = _make_provider([match])
        # Finished matches normally don't appear in get_live_matches(), but if
        # the sync loop receives one, events should still be fetched.
        provider.get_live_matches.return_value = [match]
        await _run_sync(provider)
        provider.get_match_events.assert_called_once()

    @pytest.mark.asyncio
    async def test_events_not_fetched_for_postponed(self):
        """get_match_events must NOT be called for POSTPONED matches."""
        match = _make_match(MatchStatus.POSTPONED)
        provider = _make_provider([match])
        await _run_sync(provider)
        provider.get_match_events.assert_not_called()

    @pytest.mark.asyncio
    async def test_events_not_fetched_for_cancelled(self):
        """get_match_events must NOT be called for CANCELLED matches."""
        match = _make_match(MatchStatus.CANCELLED)
        provider = _make_provider([match])
        await _run_sync(provider)
        provider.get_match_events.assert_not_called()

    @pytest.mark.asyncio
    async def test_stats_not_fetched_for_postponed(self):
        """get_match_statistics must NOT be called for POSTPONED matches."""
        match = _make_match(MatchStatus.POSTPONED)
        provider = _make_provider([match])
        await _run_sync(provider)
        provider.get_match_statistics.assert_not_called()

    @pytest.mark.asyncio
    async def test_stats_not_fetched_for_cancelled(self):
        """get_match_statistics must NOT be called for CANCELLED matches."""
        match = _make_match(MatchStatus.CANCELLED)
        provider = _make_provider([match])
        await _run_sync(provider)
        provider.get_match_statistics.assert_not_called()

    @pytest.mark.asyncio
    async def test_mixed_statuses_only_meaningful_get_events(self):
        """With a mix of SCHEDULED and LIVE matches, events are only fetched for LIVE."""
        scheduled = _make_match(MatchStatus.SCHEDULED, external_id=100)
        live = _make_match(MatchStatus.LIVE, external_id=200)
        provider = _make_provider([scheduled, live])
        await _run_sync(provider)
        assert provider.get_match_events.call_count == 1
        call_args = provider.get_match_events.call_args[0][0]
        assert call_args == 200

    @pytest.mark.asyncio
    async def test_upsert_still_persists_scheduled_match(self):
        """SCHEDULED match is still upserted to DB even without events/stats."""
        match = _make_match(MatchStatus.SCHEDULED)
        provider = _make_provider([match])
        mock_repo = await _run_sync(provider)
        mock_repo.upsert.assert_called_once()
        upsert_data = mock_repo.upsert.call_args[0][0]
        assert upsert_data["status"] == "scheduled"
