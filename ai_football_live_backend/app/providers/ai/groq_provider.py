from __future__ import annotations

import asyncio

from app.config import settings
from app.providers.ai.base import AIProvider
from app.providers.ai.errors import (
    AIProviderAuthError,
    AIProviderRateLimitError,
    AIProviderResponseError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)


class GroqAIProvider(AIProvider):
    """Real AI provider using the Groq API.

    Uses AsyncGroq with JSON Object Mode.
    Raises typed exceptions on failure; does not swallow errors.
    """

    def __init__(self) -> None:
        from groq import AsyncGroq

        api_key = settings.ai.GROQ_API_KEY
        if not api_key:
            raise AIProviderAuthError("GROQ_API_KEY is not configured")

        self._client = AsyncGroq(
            api_key=api_key,
            timeout=settings.ai.AI_TIMEOUT_SECONDS,
        )
        self._model = settings.ai.GROQ_MODEL

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = "json",
        max_tokens: int = 1024,
    ) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
                temperature=settings.ai.AI_TEMPERATURE,
            )
        except asyncio.TimeoutError as exc:
            raise AIProviderTimeoutError("Groq request timed out") from exc
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            if status is not None:
                if status == 401:
                    raise AIProviderAuthError("Invalid Groq API key") from exc
                if status == 429:
                    raise AIProviderRateLimitError("Groq rate limit exceeded") from exc
                if 500 <= status < 600:
                    raise AIProviderUnavailableError(
                        f"Groq server error: {status}"
                    ) from exc
            raise AIProviderUnavailableError(
                f"Groq request failed: {exc}"
            ) from exc

        content = response.choices[0].message.content
        if not content or not content.strip():
            raise AIProviderResponseError("Groq returned an empty response")

        return content

    def get_provider_name(self) -> str:
        return "groq"

    def get_rate_limits(self) -> dict:
        return {
            "requests_per_minute": settings.ai.GROQ_APP_MAX_REQUESTS_PER_MINUTE,
            "tokens_per_day": settings.ai.GROQ_APP_MAX_REQUESTS_PER_DAY,
        }
