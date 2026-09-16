from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import async_session
from app.database.repositories.match_repo import MatchRepository, LeagueRepository
from app.services.match_service import MatchService
from app.services.stream_service import StreamService
from app.services.ai.analysis_service import AnalysisService
from app.providers.football_data.mock_provider import MockFootballProvider
from app.providers.ai.mocks.mock_provider import MockAIProvider
from app.providers.cache.memory_provider import InMemoryCacheProvider
from app.providers.stream.authorized_provider import AuthorizedStreamProvider
from app.config import settings


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


def get_match_service(db: AsyncSession) -> MatchService:
    match_repo = MatchRepository(db)
    league_repo = LeagueRepository(db)
    return MatchService(match_repo, league_repo)


def get_stream_service(db: AsyncSession) -> StreamService:
    stream_provider = AuthorizedStreamProvider(db)
    return StreamService(stream_provider, db)


def get_analysis_service() -> AnalysisService:
    ai_provider = MockAIProvider()
    return AnalysisService(ai_provider)


def get_football_provider() -> MockFootballProvider:
    return MockFootballProvider()


def get_cache_provider() -> InMemoryCacheProvider:
    return InMemoryCacheProvider()
