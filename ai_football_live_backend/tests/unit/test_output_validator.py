import json
import pytest

from app.services.ai.output_validator import AIOutputValidator
from app.core.domain.match import Match, League, Team, MatchStatistic
from app.core.enums.match_status import MatchStatus
from app.core.domain.analysis import CalculatedMetrics


def create_test_match() -> Match:
    league = League(id=1, provider_name="mock", external_id=1001, name="Premier League")
    home_team = Team(id=1, provider_name="mock", external_id=101, name="Arsenal", short_name="ARS")
    away_team = Team(id=2, provider_name="mock", external_id=102, name="Chelsea", short_name="CHE")

    statistics = [
        MatchStatistic(id=1, match_id=1, stat_type="possession", home_value="58", away_value="42"),
    ]

    return Match(
        id=1, provider_name="mock", external_id=2001,
        league=league, home_team=home_team, away_team=away_team,
        status=MatchStatus.LIVE, match_date="2026-09-15T19:00:00Z",
        minute=67, home_score=2, away_score=1,
        statistics=statistics,
    )


class TestAIOutputValidator:
    def test_validate_structure_valid(self):
        validator = AIOutputValidator()
        output = json.dumps({
            "interpretation": "Test analysis with enough characters",
            "key_insights": ["Insight 1"],
            "data_references": [],
        })
        result, error = validator.validate_structure(output)
        assert result is not None
        assert error is None

    def test_validate_structure_invalid_json(self):
        validator = AIOutputValidator()
        result, error = validator.validate_structure("not json")
        assert result is None
        assert "Invalid JSON" in error

    def test_validate_structure_missing_field(self):
        validator = AIOutputValidator()
        output = json.dumps({"interpretation": "test"})
        result, error = validator.validate_structure(output)
        assert result is None
        assert "Missing required field" in error

    def test_validate_structure_short_interpretation(self):
        validator = AIOutputValidator()
        output = json.dumps({
            "interpretation": "short",
            "key_insights": ["test"],
            "data_references": [],
        })
        result, error = validator.validate_structure(output)
        assert result is None
        assert "at least 10 characters" in error

    def test_validate_against_source_valid(self):
        validator = AIOutputValidator()
        match = create_test_match()
        metrics = CalculatedMetrics(
            score_line="2 - 1", match_status_text="67'",
            home_score=2, away_score=1, minute=67, status="live",
        )
        output = {
            "interpretation": "The match is currently 2 - 1",
            "key_insights": ["Arsenal leads"],
            "data_references": [
                {"type": "score", "key": "score_line", "value": "2 - 1"},
                {"type": "team", "key": "home_team", "value": "Arsenal"},
            ],
        }
        result = validator.validate_against_source(output, match, metrics)
        assert result.is_valid

    def test_validate_against_source_wrong_score(self):
        validator = AIOutputValidator()
        match = create_test_match()
        metrics = CalculatedMetrics(
            score_line="2 - 1", match_status_text="67'",
            home_score=2, away_score=1, minute=67, status="live",
        )
        output = {
            "interpretation": "The match is currently 1 - 2",
            "key_insights": ["test"],
            "data_references": [
                {"type": "score", "key": "score_line", "value": "1 - 2"},
            ],
        }
        result = validator.validate_against_source(output, match, metrics)
        assert not result.is_valid

    def test_validate_against_source_unknown_team(self):
        validator = AIOutputValidator()
        match = create_test_match()
        metrics = CalculatedMetrics(
            score_line="2 - 1", match_status_text="67'",
            home_score=2, away_score=1, minute=67, status="live",
        )
        output = {
            "interpretation": "Test analysis",
            "key_insights": ["test"],
            "data_references": [
                {"type": "team", "key": "home_team", "value": "Unknown Team"},
            ],
        }
        result = validator.validate_against_source(output, match, metrics)
        assert not result.is_valid

    def test_compute_reference_validation_rate(self):
        validator = AIOutputValidator()
        match = create_test_match()
        output = {
            "data_references": [
                {"type": "score", "key": "score_line", "value": "2 - 1"},
                {"type": "team", "key": "home_team", "value": "Arsenal"},
                {"type": "team", "key": "away_team", "value": "Chelsea"},
            ],
        }
        rate, label = validator.compute_reference_validation_rate(output, match)
        assert rate == 1.0
        assert label == "high"

    def test_compute_reference_validation_rate_partial(self):
        validator = AIOutputValidator()
        match = create_test_match()
        output = {
            "data_references": [
                {"type": "score", "key": "score_line", "value": "2 - 1"},
                {"type": "team", "key": "home_team", "value": "Unknown"},
            ],
        }
        rate, label = validator.compute_reference_validation_rate(output, match)
        assert rate == 0.5
        assert label == "partial"
