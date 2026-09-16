from abc import ABC, abstractmethod

from app.core.domain.match import StreamSource


class StreamProvider(ABC):
    """Resolves authorized streams for a given match.

    This interface represents the ability to FIND an authorized stream.
    It does NOT manage stream records - that is the repository's job.
    """

    @abstractmethod
    async def resolve(self, match_id: int) -> "StreamResolution":
        ...

    @abstractmethod
    async def list_available(self, match_id: int) -> list[StreamSource]:
        ...
