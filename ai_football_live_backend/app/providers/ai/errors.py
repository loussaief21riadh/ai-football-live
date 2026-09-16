class AIProviderError(Exception):
    """Base exception for AI provider failures."""


class AIProviderAuthError(AIProviderError):
    """Invalid or missing API credentials."""


class AIProviderRateLimitError(AIProviderError):
    """Provider rate limit exceeded."""


class AIProviderTimeoutError(AIProviderError):
    """Provider request timed out."""


class AIProviderUnavailableError(AIProviderError):
    """Provider is unreachable or returned a server error."""


class AIProviderResponseError(AIProviderError):
    """Provider returned an empty or malformed response."""
