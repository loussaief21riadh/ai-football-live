import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.providers.ai.groq_provider import GroqAIProvider
from app.providers.ai.errors import (
    AIProviderAuthError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    AIProviderResponseError,
)


def _mock_response(content: str = '{"interpretation":"test","key_insights":[],"data_references":[]}'):
    choice = MagicMock()
    choice.message.content = content
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def _mock_groq_error(status_code: int = None):
    exc = Exception("groq error")
    if status_code is not None:
        exc.status_code = status_code
    return exc


class TestGroqAIProvider:
    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    def test_provider_name(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        provider = GroqAIProvider()
        assert provider.get_provider_name() == "groq"

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_generate_returns_valid_json(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=_mock_response('{"interpretation":"Match is 2 - 1","key_insights":["Arsenal leads"],"data_references":[]}')
        )
        provider = GroqAIProvider()
        result = await provider.generate("system", "user")
        data = json.loads(result)
        assert "interpretation" in data
        assert "key_insights" in data
        assert "data_references" in data

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_system_prompt_passed(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=_mock_response()
        )
        provider = GroqAIProvider()
        await provider.generate("my system prompt", "user")
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "my system prompt"

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_user_prompt_passed(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=_mock_response()
        )
        provider = GroqAIProvider()
        await provider.generate("system", "my user prompt")
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "my user prompt"

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_json_format_requested(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=_mock_response()
        )
        provider = GroqAIProvider()
        await provider.generate("system", "user")
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["response_format"] == {"type": "json_object"}

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_max_tokens_passed(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=_mock_response()
        )
        provider = GroqAIProvider()
        await provider.generate("system", "user", max_tokens=512)
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["max_tokens"] == 512

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_temperature_passed(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.5
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=_mock_response()
        )
        provider = GroqAIProvider()
        await provider.generate("system", "user")
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["temperature"] == 0.5

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_timeout_configuration(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 15
        mock_settings.ai.AI_TEMPERATURE = 0.3
        provider = GroqAIProvider()
        call_args = mock_cls.call_args
        assert call_args.kwargs["timeout"] == 15

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    def test_missing_api_key_raises(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = ""
        with pytest.raises(AIProviderAuthError, match="GROQ_API_KEY"):
            GroqAIProvider()

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_auth_failure(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            side_effect=_mock_groq_error(401)
        )
        provider = GroqAIProvider()
        with pytest.raises(AIProviderAuthError):
            await provider.generate("system", "user")

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_rate_limit(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            side_effect=_mock_groq_error(429)
        )
        provider = GroqAIProvider()
        with pytest.raises(AIProviderRateLimitError):
            await provider.generate("system", "user")

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_server_error(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            side_effect=_mock_groq_error(503)
        )
        provider = GroqAIProvider()
        with pytest.raises(AIProviderUnavailableError):
            await provider.generate("system", "user")

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_timeout(self, mock_cls, mock_settings):
        import asyncio
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            side_effect=asyncio.TimeoutError()
        )
        provider = GroqAIProvider()
        with pytest.raises(AIProviderTimeoutError):
            await provider.generate("system", "user")

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_empty_response(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=_mock_response("")
        )
        provider = GroqAIProvider()
        with pytest.raises(AIProviderResponseError, match="empty"):
            await provider.generate("system", "user")

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_whitespace_response(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=_mock_response("   ")
        )
        provider = GroqAIProvider()
        with pytest.raises(AIProviderResponseError, match="empty"):
            await provider.generate("system", "user")

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    def test_rate_limits(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.GROQ_APP_MAX_REQUESTS_PER_MINUTE = 30
        mock_settings.ai.GROQ_APP_MAX_REQUESTS_PER_DAY = 14400
        provider = GroqAIProvider()
        limits = provider.get_rate_limits()
        assert limits["requests_per_minute"] == 30
        assert limits["tokens_per_day"] == 14400
