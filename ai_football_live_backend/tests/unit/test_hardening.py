import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from app.core.domain.match import Match, League, Team, MatchEvent, MatchStatistic
from app.core.enums.match_status import MatchStatus, EventType


@pytest.fixture
def mock_league():
    return League(
        id=1, provider_name="mock", external_id=1001,
        name="Premier League", country="England", season="2026-2027",
    )


@pytest.fixture
def mock_teams():
    return (
        Team(id=1, provider_name="mock", external_id=101, name="Arsenal", short_name="ARS"),
        Team(id=2, provider_name="mock", external_id=102, name="Chelsea", short_name="CHE"),
    )


@pytest.fixture
def mock_match(mock_league, mock_teams):
    home, away = mock_teams
    return Match(
        id=1, provider_name="mock", external_id=2001,
        league=mock_league, home_team=home, away_team=away,
        status=MatchStatus.LIVE, match_date=datetime.now(timezone.utc),
        minute=67, home_score=2, away_score=1,
    )


@pytest.fixture
def mock_provider(mock_league, mock_teams, mock_match):
    home, away = mock_teams
    provider = AsyncMock()
    provider.get_leagues.return_value = [mock_league]
    provider.get_live_matches.return_value = [mock_match]
    provider.get_upcoming_matches.return_value = []
    provider.get_match_events.return_value = [
        MatchEvent(
            id=1, match_id=1, provider_name="mock",
            external_event_id="evt_101", event_type=EventType.GOAL,
            minute=23, team_id=1, player_name="Bukayo Saka",
        ),
    ]
    provider.get_match_statistics.return_value = [
        MatchStatistic(
            id=1, match_id=1, stat_type="possession",
            home_value="58", away_value="42",
        ),
    ]
    return provider


class TestSyncIdempotency:
    @pytest.mark.asyncio
    async def test_sync_does_not_depend_on_internal_ids(self, mock_provider):
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
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
                        service = DataSyncService(mock_provider)
                        await service._sync_once()

                        mock_provider.get_live_matches.assert_called_once()
                        mock_provider.get_upcoming_matches.assert_called_once_with(hours=24)
                        mock_provider.get_match_events.assert_called()
                        mock_provider.get_match_statistics.assert_called()

    @pytest.mark.asyncio
    async def test_sync_uses_provider_name_not_hardcoded(self, mock_provider, mock_league):
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
                        mock_league_repo = MagicMock()
                        mock_league_repo.upsert = AsyncMock(return_value=mock_repo_instance)
                        MockLeagueRepo.return_value = mock_league_repo
                        MockTeamRepo.return_value = MagicMock(upsert=AsyncMock(return_value=mock_repo_instance))
                        mock_match_repo = MagicMock()
                        mock_match_repo.upsert = AsyncMock(return_value=mock_repo_instance)
                        mock_match_repo.upsert_events = AsyncMock()
                        mock_match_repo.upsert_statistics = AsyncMock()
                        MockMatchRepo.return_value = mock_match_repo

                        from app.services.sync_service import DataSyncService
                        service = DataSyncService(mock_provider)
                        await service._sync_once()

                        for call in mock_league_repo.upsert.call_args_list:
                            data = call[0][0]
                            assert data["provider_name"] == "mock"


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_does_not_expose_credentials(self):
        with patch("app.api.v1.health.engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=False)
            mock_conn.execute = AsyncMock()
            mock_engine.connect.return_value = mock_conn

            from app.api.v1.health import _check_database
            result = await _check_database()

            assert "detail" not in result
            assert "password" not in str(result).lower()
            assert "postgresql" not in str(result).lower()

    @pytest.mark.asyncio
    async def test_health_redis_error_no_credentials(self):
        with patch("app.api.v1.health.settings") as mock_settings:
            mock_settings.cache.REDIS_URL = "redis://localhost:9999"

            from app.api.v1.health import _check_redis
            result = await _check_redis()

            assert "detail" not in result or "password" not in str(result).lower()


class TestCORS:
    def test_wildcard_origins_disables_credentials(self):
        with patch("app.main.settings") as mock_settings:
            mock_settings.cors.CORS_ORIGINS = "*"
            from app.main import create_app
            app = create_app()

            cors_middleware = None
            for middleware in app.user_middleware:
                if hasattr(middleware, "cls") and middleware.cls.__name__ == "CORSMiddleware":
                    cors_middleware = middleware
                    break

            assert cors_middleware is not None
            kwargs = cors_middleware.kwargs
            assert kwargs["allow_origins"] == ["*"]
            assert kwargs["allow_credentials"] is False

    def test_specific_origins_enables_credentials(self):
        with patch("app.main.settings") as mock_settings:
            mock_settings.cors.CORS_ORIGINS = "http://localhost:3000"
            from app.main import create_app
            app = create_app()

            cors_middleware = None
            for middleware in app.user_middleware:
                if hasattr(middleware, "cls") and middleware.cls.__name__ == "CORSMiddleware":
                    cors_middleware = middleware
                    break

            assert cors_middleware is not None
            kwargs = cors_middleware.kwargs
            assert kwargs["allow_credentials"] is True


class TestCacheProviderSelection:
    def test_memory_provider_default(self):
        from app.providers.cache.memory_provider import InMemoryCacheProvider

        with patch("app.api.deps.settings") as mock_settings:
            mock_settings.cache.CACHE_PROVIDER = "memory"
            from app.api.deps import get_cache_provider
            provider = get_cache_provider()
            assert isinstance(provider, InMemoryCacheProvider)

    def test_redis_provider_selects_redis(self):
        with patch("app.api.deps.settings") as mock_settings:
            mock_settings.cache.CACHE_PROVIDER = "redis"
            with patch("app.providers.cache.redis_provider.RedisCacheProvider") as MockRedis:
                MockRedis.return_value = MagicMock()
                from app.api.deps import get_cache_provider
                provider = get_cache_provider()
                MockRedis.assert_called_once()

    def test_unknown_provider_falls_back_to_memory(self):
        from app.providers.cache.memory_provider import InMemoryCacheProvider

        with patch("app.api.deps.settings") as mock_settings:
            mock_settings.cache.CACHE_PROVIDER = "unknown"
            from app.api.deps import get_cache_provider
            provider = get_cache_provider()
            assert isinstance(provider, InMemoryCacheProvider)
