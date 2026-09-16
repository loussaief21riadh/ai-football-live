from app.config import settings
from app.providers.football_data.base import FootballDataProvider
from app.providers.football.errors import FootballProviderConfigurationError


def create_football_provider() -> FootballDataProvider:
    """Create a football provider based on the FOOTBALL_PROVIDER setting.

    Supported values: mock, api-football (or api_football)
    Raises FootballProviderConfigurationError for unknown providers
    or when api-football is selected without an API key.
    """
    provider = settings.football.FOOTBALL_PROVIDER.lower().replace("-", "_")

    if provider == "mock":
        from app.providers.football_data.mock_provider import MockFootballProvider

        return MockFootballProvider()

    if provider == "api_football":
        api_key = settings.football.FOOTBALL_API_KEY
        if not api_key:
            raise FootballProviderConfigurationError(
                "FOOTBALL_API_KEY is required when FOOTBALL_PROVIDER=api-football. "
                "Set FOOTBALL_PROVIDER=mock for local development without an API key."
            )

        base_url = settings.football.FOOTBALL_API_BASE_URL
        timeout = settings.football.FOOTBALL_API_TIMEOUT_SECONDS

        league_ids = None
        raw_ids = settings.football.FOOTBALL_LEAGUE_IDS.strip()
        if raw_ids:
            league_ids = [int(x.strip()) for x in raw_ids.split(",") if x.strip()]

        season = None
        raw_season = settings.football.FOOTBALL_SEASON.strip()
        if raw_season:
            season = int(raw_season)

        from app.providers.football.api_football_provider import ApiFootballProvider

        return ApiFootballProvider(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            league_ids=league_ids,
            season=season,
        )

    raise FootballProviderConfigurationError(
        f"Unknown FOOTBALL_PROVIDER: {settings.football.FOOTBALL_PROVIDER!r}. "
        f"Supported values: mock, api-football"
    )
