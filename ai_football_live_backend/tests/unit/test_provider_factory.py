import pytest
from unittest.mock import patch

from app.providers.ai.factory import create_ai_provider
from app.providers.ai.mocks.mock_provider import MockAIProvider


class TestProviderFactory:
    @patch("app.providers.ai.factory.settings")
    def test_mock_selected(self, mock_settings):
        mock_settings.ai.AI_PROVIDER = "mock"
        provider = create_ai_provider()
        assert isinstance(provider, MockAIProvider)

    @patch("app.providers.ai.factory.settings")
    @patch("app.providers.ai.groq_provider.settings")
    def test_groq_selected(self, mock_groq_settings, mock_factory_settings):
        mock_factory_settings.ai.AI_PROVIDER = "groq"
        mock_groq_settings.ai.GROQ_API_KEY = "test-key"
        mock_groq_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_groq_settings.ai.AI_TIMEOUT_SECONDS = 30
        from app.providers.ai.groq_provider import GroqAIProvider
        provider = create_ai_provider()
        assert isinstance(provider, GroqAIProvider)

    @patch("app.providers.ai.factory.settings")
    def test_unknown_provider_raises(self, mock_settings):
        mock_settings.ai.AI_PROVIDER = "unknown"
        with pytest.raises(ValueError, match="Unknown AI_PROVIDER"):
            create_ai_provider()
