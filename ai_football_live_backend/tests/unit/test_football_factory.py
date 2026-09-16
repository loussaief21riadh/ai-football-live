import pytest
from unittest.mock import patch, MagicMock

from app.providers.football.factory import create_football_provider
from app.providers.football.api_football_provider import ApiFootballProvider
from app.providers.football_data.mock_provider import MockFootballProvider
from app.providers.football.errors import FootballProviderConfigurationError


class TestFootballFactory:
    @patch("app.providers.football.factory.settings")
    def test_mock_selected(self, mock_settings):
        mock_settings.football.FOOTBALL_PROVIDER = "mock"
        provider = create_football_provider()
        assert isinstance(provider, MockFootballProvider)

    @patch("app.providers.football.factory.settings")
    def test_api_football_selected(self, mock_settings):
        mock_settings.football.FOOTBALL_PROVIDER = "api-football"
        mock_settings.football.FOOTBALL_API_KEY = "test-key-123"
        mock_settings.football.FOOTBALL_API_BASE_URL = "https://v3.football.api-sports.io"
        mock_settings.football.FOOTBALL_API_TIMEOUT_SECONDS = 10
        mock_settings.football.FOOTBALL_LEAGUE_IDS = ""
        mock_settings.football.FOOTBALL_SEASON = ""
        provider = create_football_provider()
        assert isinstance(provider, ApiFootballProvider)

    @patch("app.providers.football.factory.settings")
    def test_api_football_normalized(self, mock_settings):
        mock_settings.football.FOOTBALL_PROVIDER = "api_football"
        mock_settings.football.FOOTBALL_API_KEY = "test-key"
        mock_settings.football.FOOTBALL_API_BASE_URL = "https://v3.football.api-sports.io"
        mock_settings.football.FOOTBALL_API_TIMEOUT_SECONDS = 10
        mock_settings.football.FOOTBALL_LEAGUE_IDS = ""
        mock_settings.football.FOOTBALL_SEASON = ""
        provider = create_football_provider()
        assert isinstance(provider, ApiFootballProvider)

    @patch("app.providers.football.factory.settings")
    def test_api_football_without_key_raises(self, mock_settings):
        mock_settings.football.FOOTBALL_PROVIDER = "api-football"
        mock_settings.football.FOOTBALL_API_KEY = ""
        with pytest.raises(FootballProviderConfigurationError, match="FOOTBALL_API_KEY"):
            create_football_provider()

    @patch("app.providers.football.factory.settings")
    def test_unknown_provider_raises(self, mock_settings):
        mock_settings.football.FOOTBALL_PROVIDER = "unknown"
        with pytest.raises(FootballProviderConfigurationError, match="Unknown FOOTBALL_PROVIDER"):
            create_football_provider()

    @patch("app.providers.football.factory.settings")
    def test_league_ids_parsing(self, mock_settings):
        mock_settings.football.FOOTBALL_PROVIDER = "api-football"
        mock_settings.football.FOOTBALL_API_KEY = "key"
        mock_settings.football.FOOTBALL_API_BASE_URL = "https://v3.football.api-sports.io"
        mock_settings.football.FOOTBALL_API_TIMEOUT_SECONDS = 10
        mock_settings.football.FOOTBALL_LEAGUE_IDS = "39,140,78"
        mock_settings.football.FOOTBALL_SEASON = ""
        provider = create_football_provider()
        assert provider._league_ids == [39, 140, 78]

    @patch("app.providers.football.factory.settings")
    def test_season_parsing(self, mock_settings):
        mock_settings.football.FOOTBALL_PROVIDER = "api-football"
        mock_settings.football.FOOTBALL_API_KEY = "key"
        mock_settings.football.FOOTBALL_API_BASE_URL = "https://v3.football.api-sports.io"
        mock_settings.football.FOOTBALL_API_TIMEOUT_SECONDS = 10
        mock_settings.football.FOOTBALL_LEAGUE_IDS = ""
        mock_settings.football.FOOTBALL_SEASON = "2026"
        provider = create_football_provider()
        assert provider._season == 2026

    @patch("app.providers.football.factory.settings")
    def test_custom_base_url(self, mock_settings):
        mock_settings.football.FOOTBALL_PROVIDER = "api-football"
        mock_settings.football.FOOTBALL_API_KEY = "key"
        mock_settings.football.FOOTBALL_API_BASE_URL = "https://custom.api.io"
        mock_settings.football.FOOTBALL_API_TIMEOUT_SECONDS = 30
        mock_settings.football.FOOTBALL_LEAGUE_IDS = ""
        mock_settings.football.FOOTBALL_SEASON = ""
        provider = create_football_provider()
        assert provider._base_url == "https://custom.api.io"
        assert provider._timeout == 30
