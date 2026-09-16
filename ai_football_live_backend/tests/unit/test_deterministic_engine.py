import pytest

from app.core.domain.match import Match, League, Team, MatchEvent, MatchStatistic
from app.core.enums.match_status import MatchStatus, EventType
from app.services.ai.deterministic_engine import DeterministicAnalysisEngine


def create_test_match(status: MatchStatus = MatchStatus.LIVE) -> Match:
    from datetime import datetime, timezone
    league = League(id=1, provider_name="mock", external_id=1001, name="Premier League")
    home_team = Team(id=1, provider_name="mock", external_id=101, name="Arsenal", short_name="ARS")
    away_team = Team(id=2, provider_name="mock", external_id=102, name="Chelsea", short_name="CHE")
    match_date = datetime(2026, 9, 15, 19, 0, 0, tzinfo=timezone.utc)

    events = [
        MatchEvent(
            id=1, match_id=1, provider_name="mock", external_event_id="evt_1",
            event_type=EventType.GOAL, minute=23, team_id=1, player_name="Bukayo Saka",
        ),
        MatchEvent(
            id=2, match_id=1, provider_name="mock", external_event_id="evt_2",
            event_type=EventType.YELLOW_CARD, minute=35, team_id=2, player_name="Enzo Fernandez",
        ),
        MatchEvent(
            id=3, match_id=1, provider_name="mock", external_event_id="evt_3",
            event_type=EventType.GOAL, minute=56, team_id=1, player_name="Kai Havertz",
        ),
    ]

    statistics = [
        MatchStatistic(id=1, match_id=1, stat_type="possession", home_value="58", away_value="42"),
        MatchStatistic(id=2, match_id=1, stat_type="shots", home_value="12", away_value="8"),
        MatchStatistic(id=3, match_id=1, stat_type="shots_on_target", home_value="6", away_value="3"),
    ]

    return Match(
        id=1, provider_name="mock", external_id=2001,
        league=league, home_team=home_team, away_team=away_team,
        status=status, match_date=match_date,
        minute=67, home_score=2, away_score=1,
        ht_home_score=1, ht_away_score=0,
        events=events, statistics=statistics,
    )


class TestDeterministicAnalysisEngine:
    def test_calculate_live_match(self):
        engine = DeterministicAnalysisEngine()
        match = create_test_match(MatchStatus.LIVE)
        metrics = engine.calculate(match)

        assert metrics.score_line == "2 - 1"
        assert metrics.match_status_text == "67'"
        assert metrics.home_score == 2
        assert metrics.away_score == 1
        assert metrics.minute == 67
        assert metrics.status == "live"

    def test_calculate_finished_match(self):
        engine = DeterministicAnalysisEngine()
        match = create_test_match(MatchStatus.FINISHED)
        metrics = engine.calculate(match)

        assert metrics.match_status_text == "Full Time"

    def test_calculate_halftime_match(self):
        engine = DeterministicAnalysisEngine()
        match = create_test_match(MatchStatus.HALFTIME)
        match.minute = 45
        metrics = engine.calculate(match)

        assert metrics.match_status_text == "Half Time"

    def test_calculate_scheduled_match(self):
        engine = DeterministicAnalysisEngine()
        match = create_test_match(MatchStatus.SCHEDULED)
        match.minute = None
        metrics = engine.calculate(match)

        assert metrics.match_status_text == "19:00"

    def test_possession_extracted(self):
        engine = DeterministicAnalysisEngine()
        match = create_test_match()
        metrics = engine.calculate(match)

        assert metrics.possession_home == 58.0
        assert metrics.possession_away == 42.0

    def test_shots_extracted(self):
        engine = DeterministicAnalysisEngine()
        match = create_test_match()
        metrics = engine.calculate(match)

        assert metrics.shots_home == 12
        assert metrics.shots_away == 8

    def test_recent_events_formatted(self):
        engine = DeterministicAnalysisEngine()
        match = create_test_match()
        metrics = engine.calculate(match)

        assert len(metrics.recent_events) == 3
        assert "23'" in metrics.recent_events[0]
        assert "Bukayo Saka" in metrics.recent_events[0]

    def test_events_count(self):
        engine = DeterministicAnalysisEngine()
        match = create_test_match()
        metrics = engine.calculate(match)

        assert metrics.events_count_home == 2
        assert metrics.events_count_away == 1

    def test_no_statistics(self):
        engine = DeterministicAnalysisEngine()
        match = create_test_match()
        match.statistics = []
        metrics = engine.calculate(match)

        assert metrics.possession_home is None
        assert metrics.possession_away is None
        assert metrics.shots_home is None
