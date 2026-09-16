from abc import ABC, abstractmethod

from app.core.domain.match import Match, League, MatchEvent, MatchStatistic


class FootballDataProvider(ABC):
    """Abstract interface for football data sources."""

    @abstractmethod
    async def get_live_matches(self) -> list[Match]:
        ...

    @abstractmethod
    async def get_upcoming_matches(self, hours: int = 24) -> list[Match]:
        ...

    @abstractmethod
    async def get_match_by_internal_id(self, match_id: int) -> Match | None:
        ...

    @abstractmethod
    async def get_match_events(self, match_id: int) -> list[MatchEvent]:
        ...

    @abstractmethod
    async def get_match_statistics(self, match_id: int) -> list[MatchStatistic]:
        ...

    @abstractmethod
    async def get_leagues(self) -> list[League]:
        ...
