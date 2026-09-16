from app.config import settings
from app.providers.ai.base import AIProvider


def create_ai_provider() -> AIProvider:
    """Create an AI provider based on the AI_PROVIDER setting.

    Supported values: mock, groq
    Raises ValueError for unknown providers.
    """
    provider = settings.ai.AI_PROVIDER.lower()

    if provider == "mock":
        from app.providers.ai.mocks.mock_provider import MockAIProvider

        return MockAIProvider()

    if provider == "groq":
        from app.providers.ai.groq_provider import GroqAIProvider

        return GroqAIProvider()

    raise ValueError(
        f"Unknown AI_PROVIDER: {provider!r}. "
        f"Supported values: mock, groq"
    )
