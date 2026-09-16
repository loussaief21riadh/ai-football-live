from enum import Enum


class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    TIMELINE = "timeline"
    LIVE = "live"
    HALFTIME = "halftime"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"

    @classmethod
    def from_str(cls, value: str | None) -> "MatchStatus":
        if value is None:
            return cls.UNKNOWN
        for member in cls:
            if member.value == value:
                return member
        return cls.UNKNOWN


class EventType(str, Enum):
    GOAL = "goal"
    OWN_GOAL = "own_goal"
    PENALTY_SCORED = "penalty_scored"
    PENALTY_MISSED = "penalty_missed"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    SUBSTITUTION = "substitution"
    VAR_DECISION = "var_decision"
    INJURY = "injury"
    UNKNOWN = "unknown"

    @classmethod
    def from_str(cls, value: str | None) -> "EventType":
        if value is None:
            return cls.UNKNOWN
        for member in cls:
            if member.value == value:
                return member
        return cls.UNKNOWN


class AnalysisType(str, Enum):
    PRE_MATCH = "pre_match"
    LIVE = "live"
    POST_MATCH = "post_match"
    UNKNOWN = "unknown"

    @classmethod
    def from_str(cls, value: str | None) -> "AnalysisType":
        if value is None:
            return cls.UNKNOWN
        for member in cls:
            if member.value == value:
                return member
        return cls.UNKNOWN


class StreamAuthorizationStatus(str, Enum):
    AUTHORIZED = "authorized"
    UNAVAILABLE = "unavailable"
    PENDING = "pending"
    UNKNOWN = "unknown"

    @classmethod
    def from_str(cls, value: str | None) -> "StreamAuthorizationStatus":
        if value is None:
            return cls.UNKNOWN
        for member in cls:
            if member.value == value:
                return member
        return cls.UNKNOWN
