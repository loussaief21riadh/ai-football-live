from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://localhost:5432/ai_football_live"


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    AI_PROVIDER: str = "mock"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = ""
    GROQ_BASE_URL: str = ""
    GROQ_APP_MAX_REQUESTS_PER_MINUTE: int = 30
    GROQ_APP_MAX_REQUESTS_PER_DAY: int = 14400

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = ""
    GEMINI_APP_MAX_REQUESTS_PER_MINUTE: int = 15
    GEMINI_APP_MAX_REQUESTS_PER_DAY: int = 1000000


class CacheSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    CACHE_PROVIDER: str = "memory"
    REDIS_URL: str = "redis://localhost:6379"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database: DatabaseSettings = DatabaseSettings()
    ai: AISettings = AISettings()
    cache: CacheSettings = CacheSettings()


settings = Settings()
