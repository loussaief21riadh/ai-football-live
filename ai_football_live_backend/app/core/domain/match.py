from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.core.enums.match_status import EventType, MatchStatus


@dataclass
class Team:
    id: int | None
    provider_name: str
    external_id: int
    name: str
    short_name: str | None = None
    logo_url: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class League:
    id: int | None
    provider_name: str
    external_id: int
    name: str
    country: str | None = None
    logo_url: str | None = None
    season: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MatchEvent:
    id: int | None
    match_id: int
    provider_name: str
    external_event_id: str | None
    event_type: EventType
    minute: int
    added_time: int | None = None
    team_id: int | None = None
    player_name: str | None = None
    assist_player: str | None = None
    detail: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MatchStatistic:
    id: int | None
    match_id: int
    stat_type: str
    home_value: str | None = None
    away_value: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class StreamSource:
    id: int | None
    match_id: int
    provider_name: str
    stream_url: str
    embed_url: str | None = None
    is_active: bool = True
    authorization_status: str = "pending"
    legal_basis: str = ""
    authorized_by: str | None = None
    authorized_at: datetime | None = None
    quality: str | None = None
    language: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AIAnalysis:
    id: int | None
    match_id: int
    analysis_type: str
    context_fingerprint: str
    interpretation: str
    key_insights: list[str] = field(default_factory=list)
    reference_validation_rate: float = 0.0
    validation_label: str = "low"
    data_references: list[dict] = field(default_factory=list)
    validation_result: str = "pending"
    ai_provider: str = "mock"
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None
    version: int = 1


@dataclass
class Match:
    id: int | None
    provider_name: str
    external_id: int
    league: League
    home_team: Team
    away_team: Team
    status: MatchStatus
    match_date: datetime
    venue: str | None = None
    referee: str | None = None
    minute: int | None = None
    added_time: int | None = None
    home_score: int = 0
    away_score: int = 0
    ht_home_score: int | None = None
    ht_away_score: int | None = None
    events: list[MatchEvent] = field(default_factory=list)
    statistics: list[MatchStatistic] = field(default_factory=list)
    streams: list[StreamSource] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
