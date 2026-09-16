from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = "json",
        max_tokens: int = 1024,
    ) -> str:
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...

    def get_rate_limits(self) -> dict:
        return {"requests_per_minute": None, "tokens_per_day": None}
