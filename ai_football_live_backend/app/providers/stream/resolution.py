from dataclasses import dataclass

from app.core.domain.match import StreamSource


@dataclass
class StreamResolution:
    """Result of stream resolution.

    Attributes:
        available: Whether an authorized stream was found.
        stream: The best authorized StreamSource, or None if unavailable.
        message: Human-readable status message for Flutter display.
        alternatives: Number of other authorized streams available.
    """

    available: bool
    stream: StreamSource | None
    message: str
    alternatives: int = 0
