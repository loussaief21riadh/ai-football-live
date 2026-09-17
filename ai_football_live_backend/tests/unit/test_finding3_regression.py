import pytest
from unittest.mock import AsyncMock, patch, MagicMock

import httpx

from app.providers.football.api_football_provider import ApiFootballProvider
from app.providers.football.errors import (
    FootballProviderAuthenticationError,
    FootballProviderRateLimitError,
    FootballProviderTimeoutError,
    FootballProviderNetworkError,
    FootballProviderResponseError,
)


def _mock_httpx_response(status_code: int = 200, json_data: dict | None = None, headers: dict | None = None):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    response.headers = headers or {}
    return response


class TestFinding3Retry:
    """Regression tests for Finding 3: bounded retry on rate-limit errors."""

    @pytest.mark.asyncio
    async def test_retry_succeeds_after_rate_limit(self):
        """First request returns 429, second returns 200 → provider returns data."""
        provider = ApiFootballProvider(api_key="key")
        rate_limit_response = _mock_httpx_response(429, headers={"Retry-After": "5"})
        success_response = _mock_httpx_response(200, {"response": []})

        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=[rate_limit_response, success_response])
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with patch("app.providers.football.api_football_provider.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                result = await provider.get_live_matches()

            assert result == []
            assert mock_instance.get.call_count == 2
            mock_sleep.assert_called_once_with(5)

    @pytest.mark.asyncio
    async def test_retry_exhausted_raises(self):
        """All attempts return 429 → FootballProviderRateLimitError after MAX_RETRIES."""
        provider = ApiFootballProvider(api_key="key")
        rate_limit_response = _mock_httpx_response(429, headers={"Retry-After": "1"})

        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=rate_limit_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with patch("app.providers.football.api_football_provider.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                with pytest.raises(FootballProviderRateLimitError) as exc_info:
                    await provider.get_live_matches()

            assert mock_instance.get.call_count == provider.MAX_RETRIES
            assert mock_sleep.call_count == provider.MAX_RETRIES - 1
            assert exc_info.value.retry_after == 1

    @pytest.mark.asyncio
    async def test_retry_respects_retry_after_duration(self):
        """Retry-After: 5 → sleep called with 5 seconds."""
        provider = ApiFootballProvider(api_key="key")
        rate_limit_response = _mock_httpx_response(429, headers={"Retry-After": "5"})
        success_response = _mock_httpx_response(200, {"response": []})

        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=[rate_limit_response, success_response])
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with patch("app.providers.football.api_football_provider.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                await provider.get_live_matches()

            mock_sleep.assert_called_once_with(5)

    @pytest.mark.asyncio
    async def test_retry_without_retry_after_uses_default(self):
        """429 without Retry-After → fallback delay (30s) used."""
        provider = ApiFootballProvider(api_key="key")
        rate_limit_response = _mock_httpx_response(429)
        success_response = _mock_httpx_response(200, {"response": []})

        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=[rate_limit_response, success_response])
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with patch("app.providers.football.api_football_provider.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                await provider.get_live_matches()

            mock_sleep.assert_called_once_with(provider.RETRY_FALLBACK_DELAY)

    @pytest.mark.asyncio
    async def test_retry_caps_excessive_retry_after(self):
        """Retry-After: 300 → capped to RETRY_MAX_DELAY (60s)."""
        provider = ApiFootballProvider(api_key="key")
        rate_limit_response = _mock_httpx_response(429, headers={"Retry-After": "300"})
        success_response = _mock_httpx_response(200, {"response": []})

        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=[rate_limit_response, success_response])
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with patch("app.providers.football.api_football_provider.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                await provider.get_live_matches()

            mock_sleep.assert_called_once_with(provider.RETRY_MAX_DELAY)

    @pytest.mark.asyncio
    async def test_auth_errors_not_retried(self):
        """401/403 → FootballProviderAuthenticationError raised immediately, no retry."""
        provider = ApiFootballProvider(api_key="key")

        for status in (401, 403):
            with patch.object(httpx, "AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(return_value=_mock_httpx_response(status))
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=False)
                mock_client.return_value = mock_instance

                with pytest.raises(FootballProviderAuthenticationError):
                    await provider.get_live_matches()
                assert mock_instance.get.call_count == 1

    @pytest.mark.asyncio
    async def test_server_errors_not_retried(self):
        """HTTP 500 → FootballProviderResponseError raised immediately, no retry."""
        provider = ApiFootballProvider(api_key="key")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=_mock_httpx_response(500))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderResponseError):
                await provider.get_live_matches()
            assert mock_instance.get.call_count == 1

    @pytest.mark.asyncio
    async def test_timeout_not_retried(self):
        """Timeout → FootballProviderTimeoutError raised immediately, no retry."""
        provider = ApiFootballProvider(api_key="key")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=httpx.TimeoutException("timed out"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderTimeoutError):
                await provider.get_live_matches()
            assert mock_instance.get.call_count == 1

    @pytest.mark.asyncio
    async def test_network_error_not_retried(self):
        """Connection error → FootballProviderNetworkError raised immediately, no retry."""
        provider = ApiFootballProvider(api_key="key")
        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=httpx.ConnectError("connection refused"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with pytest.raises(FootballProviderNetworkError):
                await provider.get_live_matches()
            assert mock_instance.get.call_count == 1

    @pytest.mark.asyncio
    async def test_api_key_not_in_logs_during_retry(self):
        """Retry behavior must not leak the API key in logs or exceptions."""
        provider = ApiFootballProvider(api_key="super-secret-key-12345")
        rate_limit_response = _mock_httpx_response(429, headers={"Retry-After": "1"})
        success_response = _mock_httpx_response(200, {"response": []})

        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=[rate_limit_response, success_response])
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance

            with patch("app.providers.football.api_football_provider.asyncio.sleep", new_callable=AsyncMock):
                result = await provider.get_live_matches()

            assert result == []
            assert mock_instance.get.call_count == 2
