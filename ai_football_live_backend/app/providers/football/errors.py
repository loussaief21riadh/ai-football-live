class FootballProviderError(Exception):
    """Base exception for football provider failures."""


class FootballProviderConfigurationError(FootballProviderError):
    """Missing or invalid provider configuration."""


class FootballProviderAuthenticationError(FootballProviderError):
    """Invalid or missing API credentials (HTTP 401/403)."""


class FootballProviderRateLimitError(FootballProviderError):
    """Provider rate limit exceeded (HTTP 429)."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class FootballProviderTimeoutError(FootballProviderError):
    """Provider request timed out."""


class FootballProviderNetworkError(FootballProviderError):
    """Provider is unreachable (connection error)."""


class FootballProviderResponseError(FootballProviderError):
    """Provider returned a malformed or invalid response."""
