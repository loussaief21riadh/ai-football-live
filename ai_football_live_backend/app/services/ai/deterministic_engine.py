from app.core.domain.match import Match, MatchEvent
from app.core.domain.analysis import CalculatedMetrics
from app.core.enums.match_status import MatchStatus, EventType


class DeterministicAnalysisEngine:
    """Formats and extracts factual metrics from provider data.

    This engine performs ZERO heuristic computation.
    All output is directly traceable to provider data.
    """

    def calculate(self, match: Match) -> CalculatedMetrics:
        stats = {s.stat_type: s for s in match.statistics}
        possession = self._extract_possession(stats)

        return CalculatedMetrics(
            score_line=f"{match.home_score} - {match.away_score}",
            match_status_text=self._format_status(match),
            home_score=match.home_score,
            away_score=match.away_score,
            minute=match.minute,
            status=match.status.value,
            possession_home=possession[0],
            possession_away=possession[1],
            shots_home=self._extract_stat_int(stats, "shots", 0),
            shots_away=self._extract_stat_int(stats, "shots", 1),
            shots_on_target_home=self._extract_stat_int(stats, "shots_on_target", 0),
            shots_on_target_away=self._extract_stat_int(stats, "shots_on_target", 1),
            corners_home=self._extract_stat_int(stats, "corners", 0),
            corners_away=self._extract_stat_int(stats, "corners", 1),
            recent_events=self._format_recent_events(match.events, n=5),
            events_count_home=sum(1 for e in match.events if e.team_id == match.home_team.id),
            events_count_away=sum(1 for e in match.events if e.team_id == match.away_team.id),
        )

    def _format_status(self, match: Match) -> str:
        if match.status == MatchStatus.FINISHED:
            return "Full Time"
        if match.status == MatchStatus.HALFTIME:
            return "Half Time"
        if match.status == MatchStatus.LIVE and match.minute is not None:
            base = str(match.minute)
            if match.added_time:
                base = f"{match.minute}+{match.added_time}"
            return f"{base}'"
        if match.status == MatchStatus.SCHEDULED:
            return match.match_date.strftime("%H:%M")
        return match.status.value

    def _format_recent_events(self, events: list[MatchEvent], n: int = 5) -> list[str]:
        recent = events[-n:] if len(events) >= n else events
        return [self._format_event(e) for e in recent]

    def _format_event(self, event: MatchEvent) -> str:
        minute = f"{event.minute}'"
        type_label = {
            EventType.GOAL: "Goal",
            EventType.OWN_GOAL: "Own Goal",
            EventType.PENALTY_SCORED: "Penalty Goal",
            EventType.PENALTY_MISSED: "Penalty Missed",
            EventType.YELLOW_CARD: "Yellow Card",
            EventType.RED_CARD: "Red Card",
            EventType.SUBSTITUTION: "Substitution",
        }.get(event.event_type, event.event_type.value)

        parts = [minute, type_label, event.player_name or "Unknown"]
        if event.assist_player:
            parts.append(f"(Assist: {event.assist_player})")
        if event.detail:
            parts.append(f"({event.detail})")
        return " - ".join(parts)

    def _extract_possession(self, stats: dict) -> tuple[float | None, float | None]:
        stat = stats.get("possession")
        if stat is None:
            return (None, None)
        try:
            return (float(stat.home_value), float(stat.away_value))
        except (ValueError, TypeError):
            return (None, None)

    def _extract_stat_int(self, stats: dict, stat_type: str, index: int) -> int | None:
        stat = stats.get(stat_type)
        if stat is None:
            return None
        values = [stat.home_value, stat.away_value]
        try:
            return int(values[index])
        except (ValueError, TypeError, IndexError):
            return None
