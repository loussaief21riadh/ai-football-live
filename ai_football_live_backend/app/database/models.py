from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LeagueModel(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_name = Column(String(50), nullable=False)
    external_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    country = Column(String(100))
    logo_url = Column(Text)
    season = Column(String(20))
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    __table_args__ = (
        UniqueConstraint("provider_name", "external_id", name="uq_league_provider_external"),
    )

    matches = relationship("MatchModel", back_populates="league")


class TeamModel(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_name = Column(String(50), nullable=False)
    external_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    short_name = Column(String(10))
    logo_url = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    __table_args__ = (
        UniqueConstraint("provider_name", "external_id", name="uq_team_provider_external"),
    )


class MatchModel(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_name = Column(String(50), nullable=False, default="api_football")
    external_id = Column(Integer, nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    status = Column(String(20), nullable=False, default="scheduled")
    minute = Column(Integer)
    added_time = Column(Integer)
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    ht_home_score = Column(Integer)
    ht_away_score = Column(Integer)
    match_date = Column(DateTime(timezone=True), nullable=False)
    venue = Column(String(255))
    referee = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    __table_args__ = (
        UniqueConstraint("provider_name", "external_id", name="uq_match_provider_external"),
        Index("idx_matches_status", "status"),
        Index("idx_matches_date", "match_date"),
        Index("idx_matches_league", "league_id"),
    )

    league = relationship("LeagueModel", back_populates="matches")
    home_team = relationship("TeamModel", foreign_keys=[home_team_id])
    away_team = relationship("TeamModel", foreign_keys=[away_team_id])
    events = relationship("MatchEventModel", back_populates="match", cascade="all, delete-orphan")
    statistics = relationship("MatchStatisticModel", back_populates="match", cascade="all, delete-orphan")
    streams = relationship("StreamSourceModel", back_populates="match", cascade="all, delete-orphan")
    analyses = relationship("AIAnalysisModel", back_populates="match", cascade="all, delete-orphan")


class MatchEventModel(Base):
    __tablename__ = "match_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    provider_name = Column(String(50), nullable=False, default="api_football")
    external_event_id = Column(String(100))
    event_type = Column(String(30), nullable=False)
    minute = Column(Integer, nullable=False)
    added_time = Column(Integer)
    team_id = Column(Integer, ForeignKey("teams.id"))
    player_name = Column(String(255))
    assist_player = Column(String(255))
    detail = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (
        Index("idx_events_match", "match_id"),
    )

    match = relationship("MatchModel", back_populates="events")


class MatchStatisticModel(Base):
    __tablename__ = "match_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    stat_type = Column(String(50), nullable=False)
    home_value = Column(String(50))
    away_value = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (
        UniqueConstraint("match_id", "stat_type", name="uq_match_stat_type"),
    )

    match = relationship("MatchModel", back_populates="statistics")


class StreamSourceModel(Base):
    __tablename__ = "stream_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    provider_name = Column(String(100), nullable=False)
    stream_url = Column(Text, nullable=False)
    embed_url = Column(Text)
    is_active = Column(Boolean, default=True)
    authorization_status = Column(String(20), nullable=False, default="pending")
    legal_basis = Column(Text, nullable=False, default="")
    authorized_by = Column(String(255))
    authorized_at = Column(DateTime(timezone=True))
    quality = Column(String(20))
    language = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    __table_args__ = (
        Index("idx_stream_match", "match_id", "is_active", "authorization_status"),
    )

    match = relationship("MatchModel", back_populates="streams")


class AIAnalysisModel(Base):
    __tablename__ = "ai_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    analysis_type = Column(String(50), nullable=False)
    context_fingerprint = Column(String(64), nullable=False)
    interpretation = Column(Text, nullable=False)
    key_insights = Column(Text, default="[]")
    reference_validation_rate = Column(Integer, default=0)
    validation_label = Column(String(20), default="low")
    data_references = Column(Text, default="[]")
    validation_result = Column(String(20), default="pending")
    ai_provider = Column(String(50), nullable=False, default="mock")
    generated_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True))
    version = Column(Integer, default=1)

    __table_args__ = (
        Index("idx_ai_analysis_match", "match_id", "analysis_type"),
    )

    match = relationship("MatchModel", back_populates="analyses")
