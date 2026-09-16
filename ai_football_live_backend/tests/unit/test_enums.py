import pytest
from datetime import datetime, timezone

from app.core.enums.match_status import MatchStatus, EventType, AnalysisType, StreamAuthorizationStatus
from app.core.enums.error_codes import ErrorCode, ERROR_STATUS_MAP


class TestMatchStatus:
    def test_from_str_valid(self):
        assert MatchStatus.from_str("live") == MatchStatus.LIVE
        assert MatchStatus.from_str("scheduled") == MatchStatus.SCHEDULED
        assert MatchStatus.from_str("finished") == MatchStatus.FINISHED

    def test_from_str_none(self):
        assert MatchStatus.from_str(None) == MatchStatus.UNKNOWN

    def test_from_str_unknown(self):
        assert MatchStatus.from_str("invalid") == MatchStatus.UNKNOWN


class TestEventType:
    def test_from_str_valid(self):
        assert EventType.from_str("goal") == EventType.GOAL
        assert EventType.from_str("yellow_card") == EventType.YELLOW_CARD

    def test_from_str_none(self):
        assert EventType.from_str(None) == EventType.UNKNOWN

    def test_from_str_unknown(self):
        assert EventType.from_str("invalid") == EventType.UNKNOWN


class TestAnalysisType:
    def test_from_str_valid(self):
        assert AnalysisType.from_str("pre_match") == AnalysisType.PRE_MATCH
        assert AnalysisType.from_str("live") == AnalysisType.LIVE

    def test_from_str_none(self):
        assert AnalysisType.from_str(None) == AnalysisType.UNKNOWN


class TestStreamAuthorizationStatus:
    def test_from_str_valid(self):
        assert StreamAuthorizationStatus.from_str("authorized") == StreamAuthorizationStatus.AUTHORIZED

    def test_from_str_none(self):
        assert StreamAuthorizationStatus.from_str(None) == StreamAuthorizationStatus.UNKNOWN


class TestErrorCode:
    def test_all_codes_have_status_mapping(self):
        for code in ErrorCode:
            assert code in ERROR_STATUS_MAP, f"Missing status mapping for {code}"

    def test_match_not_found_is_404(self):
        assert ERROR_STATUS_MAP[ErrorCode.MATCH_NOT_FOUND] == 404

    def test_stream_unavailable_is_200(self):
        assert ERROR_STATUS_MAP[ErrorCode.STREAM_UNAVAILABLE] == 200

    def test_ai_validation_failed_is_200(self):
        assert ERROR_STATUS_MAP[ErrorCode.AI_VALIDATION_FAILED] == 200
