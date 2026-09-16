import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import httpx

from app.providers.football.api_football_provider import (
    ApiFootballProvider, PROVIDER_NAME, STATUS_MAP, EVENT_TYPE_MAP,
)
from app.providers.football.errors import (
    FootballProviderConfigurationError,
    FootballProviderAuthenticationError,
    FootballProviderRateLimitError,
    FootballProviderTimeoutError,
    FootballProviderNetworkError,
    FootballProviderResponseError,
)
from app.core.enums.match_status import MatchStatus, EventType

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _load_fixture(name: str) -> dict:
    path = FIXTURES_DIR / f"api_football_{name}.json"
    with open(path) as f:
        return json.load(f)


def _mock_httpx_response(status_code: int = 200, json_data: dict | None = None, headers: dict | None = None):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    response.headers = headers or {}
    return response


class TestConfiguration:
    def test_missing_api_key_raises(self):
        with pytest.raises(FootballProviderConfigurationError, match="FOOTBALL_API_KEY"):
            ApiFootballProvider(api_key="")

    def test_empty_api_key_raises(self):
        with pytest.raises(FootballProviderConfigurationError):
            ApiFootballProvider(api_key="")

    def test_valid_config(self):
        provider = ApiFootballProvider(api_key="test-key-123")
        assert provider._api_key == "test-key-123"
        assert provider._base_url == "https://v3.football.api-sports.io"
        assert provider._timeout == 10

    def test_custom_config(self):
        provider = ApiFootballProvider(
            api_key="key",
            base_url="https://custom.api.io",
            timeout=30,
            league_ids=[39, 140],
            season=2026,
        )
        assert provider._base_url == "https://custom.api.io"
        assert provider._timeout == 30
        assert provider._league_ids == [39, 140]
        assert provider._season == 2026

    def test_trailing_slash_stripped(self):
        provider = ApiFootballProvider(api_key="key", base_url="https://api.io/")
        assert provider._base_url == "https://api.io"


class TestAuthentication:
    @pytest.mark.asyncio
    async def test_401_raises_auth_error(self):
        provider = ApiFootballProvider(api_key="bad-key")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(401))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderAuthenticationError):
                await provider.get_live_matches()

    @pytest.mark.asyncio
    async def test_403_raises_auth_error(self):
        provider = ApiFootballProvider(api_key="bad-key")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(403))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderAuthenticationError):
                await provider.get_live_matches()

    @pytest.mark.asyncio
    async def test_api_error_token_raises_auth_error(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("auth_error")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderAuthenticationError):
                await provider.get_live_matches()

    @pytest.mark.asyncio
    async def test_headers_include_api_key(self):
        provider = ApiFootballProvider(api_key="secret-key-123")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = _mock_httpx_response(200, _load_fixture("empty"))
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            await provider.get_live_matches()

            call_args = mock_instance.get.call_args
            headers = call_args[1]["headers"] if "headers" in call_args[1] else call_args[0][2] if len(call_args[0]) > 2 else {}
            assert headers.get("x-apisports-key") == "secret-key-123"
            assert headers.get("Accept") == "application/json"


class TestRateLimit:
    @pytest.mark.asyncio
    async def test_429_raises_rate_limit(self):
        provider = ApiFootballProvider(api_key="key")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(429))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderRateLimitError):
                await provider.get_live_matches()

    @pytest.mark.asyncio
    async def test_429_with_retry_after(self):
        provider = ApiFootballProvider(api_key="key")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(
                return_value=_mock_httpx_response(429, headers={"Retry-After": "60"})
            )
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderRateLimitError) as exc_info:
                await provider.get_live_matches()
            assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_api_ratelimit_error(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("rate_limit")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderRateLimitError):
                await provider.get_live_matches()


class TestNetworkErrors:
    @pytest.mark.asyncio
    async def test_timeout_raises_timeout_error(self):
        provider = ApiFootballProvider(api_key="key")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=httpx.TimeoutException("timed out"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderTimeoutError):
                await provider.get_live_matches()

    @pytest.mark.asyncio
    async def test_connection_error_raises_network_error(self):
        provider = ApiFootballProvider(api_key="key")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=httpx.ConnectError("connection refused"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderNetworkError):
                await provider.get_live_matches()

    @pytest.mark.asyncio
    async def test_http_500_raises_response_error(self):
        provider = ApiFootballProvider(api_key="key")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(500))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderResponseError):
                await provider.get_live_matches()


class TestResponseValidation:
    @pytest.mark.asyncio
    async def test_malformed_json_raises_response_error(self):
        provider = ApiFootballProvider(api_key="key")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderResponseError, match="invalid JSON"):
                await provider.get_live_matches()


class TestLiveMatchesMapping:
    @pytest.mark.asyncio
    async def test_live_matches_parsed(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("live")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            matches = await provider.get_live_matches()

            assert len(matches) == 2
            m1 = matches[0]
            assert m1.external_id == 1123456
            assert m1.provider_name == PROVIDER_NAME
            assert m1.status == MatchStatus.LIVE
            assert m1.home_team.name == "Arsenal"
            assert m1.away_team.name == "Chelsea"
            assert m1.league.name == "Premier League"
            assert m1.league.external_id == 39
            assert m1.home_score == 2
            assert m1.away_score == 1
            assert m1.minute == 67
            assert m1.venue == "Emirates Stadium"
            assert m1.referee == "Michael Oliver"

    @pytest.mark.asyncio
    async def test_live_matches_empty(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("empty")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            matches = await provider.get_live_matches()
            assert len(matches) == 0

    @pytest.mark.asyncio
    async def test_league_filtering(self):
        provider = ApiFootballProvider(api_key="key", league_ids=[39])
        fixture = _load_fixture("live")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            matches = await provider.get_live_matches()
            assert len(matches) == 1
            assert matches[0].league.external_id == 39


class TestStatusMapping:
    @pytest.mark.asyncio
    async def test_halftime_status(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("live")
        fixture["response"][0]["fixture"]["status"]["short"] = "HT"
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            matches = await provider.get_live_matches()
            assert matches[0].status == MatchStatus.HALFTIME

    @pytest.mark.asyncio
    async def test_finished_status(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("finished")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            matches = await provider.get_match_by_internal_id(1123456)
            assert matches.status == MatchStatus.FINISHED

    @pytest.mark.asyncio
    async def test_not_started_status(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("scheduled")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            matches = await provider.get_upcoming_matches(hours=24)
            assert matches[0].status == MatchStatus.SCHEDULED


class TestScoreMapping:
    @pytest.mark.asyncio
    async def test_halftime_scores(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("live")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            matches = await provider.get_live_matches()
            m = matches[0]
            assert m.ht_home_score == 1
            assert m.ht_away_score == 0


class TestEventsMapping:
    @pytest.mark.asyncio
    async def test_events_parsed(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("events")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            events = await provider.get_match_events(1123456)

            assert len(events) == 6
            assert events[0].event_type == EventType.GOAL
            assert events[0].minute == 23
            assert events[0].player_name == "Bukayo Saka"
            assert events[0].assist_player == "Martin Odegaard"
            assert events[0].team_id == 42

            assert events[1].event_type == EventType.YELLOW_CARD
            assert events[1].player_name == "Enzo Fernandez"

            assert events[4].event_type == EventType.VAR_DECISION

            assert events[5].event_type == EventType.SUBSTITUTION

    @pytest.mark.asyncio
    async def test_events_mixed_types(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("events_mixed")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            events = await provider.get_match_events(1123459)

            assert events[0].event_type == EventType.GOAL
            assert events[0].detail == "Normal Goal"
            assert events[1].event_type == EventType.PENALTY_SCORED
            assert events[2].event_type == EventType.OWN_GOAL

    @pytest.mark.asyncio
    async def test_events_extra_time(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("events")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            events = await provider.get_match_events(1123456)
            assert events[3].added_time == 3

    @pytest.mark.asyncio
    async def test_events_empty(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = {"response": []}
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            events = await provider.get_match_events(999)
            assert len(events) == 0


class TestStatisticsMapping:
    @pytest.mark.asyncio
    async def test_statistics_parsed(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("statistics")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            stats = await provider.get_match_statistics(1123456)

            assert len(stats) > 0
            possession = next(s for s in stats if s.stat_type == "Ball Possession")
            assert possession.home_value == "58%"
            assert possession.away_value == "42%"

            shots = next(s for s in stats if s.stat_type == "Total Shots")
            assert shots.home_value == "12"
            assert shots.away_value == "8"

    @pytest.mark.asyncio
    async def test_statistics_null_values(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("null_statistics")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            stats = await provider.get_match_statistics(1123458)

            assert len(stats) > 0
            for stat in stats:
                assert stat.home_value is None
                assert stat.away_value is None


class TestLeaguesMapping:
    @pytest.mark.asyncio
    async def test_leagues_parsed(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("leagues")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            leagues = await provider.get_leagues()

            assert len(leagues) == 2
            assert leagues[0].name == "Premier League"
            assert leagues[0].external_id == 39
            assert leagues[0].country == "England"
            assert leagues[0].provider_name == PROVIDER_NAME
            assert leagues[1].name == "La Liga"


class TestMatchById:
    @pytest.mark.asyncio
    async def test_match_found(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("finished")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            match = await provider.get_match_by_internal_id(1123456)
            assert match is not None
            assert match.external_id == 1123456
            assert match.status == MatchStatus.FINISHED

    @pytest.mark.asyncio
    async def test_match_not_found(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("empty")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            match = await provider.get_match_by_internal_id(999)
            assert match is None


class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_missing_venue(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("live")
        fixture["response"][0]["fixture"]["venue"] = {}
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            matches = await provider.get_live_matches()
            assert matches[0].venue is None

    @pytest.mark.asyncio
    async def test_missing_referee(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("live")
        fixture["response"][0]["fixture"]["referee"] = None
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            matches = await provider.get_live_matches()
            assert matches[0].referee is None

    @pytest.mark.asyncio
    async def test_null_goals(self):
        provider = ApiFootballProvider(api_key="key")
        fixture = _load_fixture("scheduled")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(200, fixture))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            matches = await provider.get_upcoming_matches(hours=24)
            assert matches[0].home_score == 0
            assert matches[0].away_score == 0


class TestSyncIntegration:
    @pytest.mark.asyncio
    async def test_sync_uses_provider_methods(self):
        provider = ApiFootballProvider(api_key="key")
        live_fixture = _load_fixture("live")
        scheduled_fixture = _load_fixture("scheduled")
        events_fixture = _load_fixture("events")
        stats_fixture = _load_fixture("statistics")

        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()

            def side_effect(url, **kwargs):
                path = str(url)
                if "live=all" in path or ("fixtures" in path and "live" in str(kwargs.get("params", {}))):
                    return _mock_httpx_response(200, live_fixture)
                elif "next" in str(kwargs.get("params", {})):
                    return _mock_httpx_response(200, scheduled_fixture)
                elif "events" in path:
                    return _mock_httpx_response(200, events_fixture)
                elif "statistics" in path:
                    return _mock_httpx_response(200, stats_fixture)
                elif "leagues" in path:
                    return _mock_httpx_response(200, _load_fixture("leagues"))
                return _mock_httpx_response(200, {"response": []})

            mock_instance.get = AsyncMock(side_effect=side_effect)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            live = await provider.get_live_matches()
            upcoming = await provider.get_upcoming_matches(hours=24)

            assert len(live) == 2
            assert len(upcoming) == 1
