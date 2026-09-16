from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://localhost:5432/ai_football_live"


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    AI_PROVIDER: str = "mock"
    AI_TIMEOUT_SECONDS: int = 30
    AI_TEMPERATURE: float = 0.3

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"
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


class FootballSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    FOOTBALL_PROVIDER: str = "mock"
    FOOTBALL_API_KEY: str = ""
    FOOTBALL_API_BASE_URL: str = "https://v3.football.api-sports.io"
    FOOTBALL_API_TIMEOUT_SECONDS: int = 10
    FOOTBALL_POLL_INTERVAL_SECONDS: int = 900
    FOOTBALL_LEAGUE_IDS: str = ""
    FOOTBALL_SEASON: str = ""


class CORSSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    CORS_ORIGINS: str = "*"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database: DatabaseSettings = DatabaseSettings()
    ai: AISettings = AISettings()
    football: FootballSettings = FootballSettings()
    cache: CacheSettings = CacheSettings()
    cors: CORSSettings = CORSSettings()


settings = Settings()
