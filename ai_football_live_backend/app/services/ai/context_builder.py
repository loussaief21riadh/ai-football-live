import json
from datetime import datetime, timezone

from app.core.domain.match import Match
from app.core.domain.analysis import CalculatedMetrics


class AIContextBuilder:
    """Builds the context provided to the LLM.

    Context contains only factual data from the provider.
    The LLM must not invent data beyond this context.
    """

    def build_system_prompt(self) -> str:
        return """You are a football match analysis assistant.

STRICT RULES:
1. You may ONLY reference facts explicitly present in the provided match data.
2. You must NOT invent statistics, scores, player names, or events.
3. You must NOT calculate or derive statistics not already provided.
4. You must NOT make predictions about future events.
5. You must NOT reference external knowledge about teams or players.
6. Every claim you make must be traceable to a specific field in the provided data.

The data you receive contains:
- match: Official match information (score, status, teams, venue)
- calculated_metrics: Pre-formatted factual summaries (score line, status text, recent events)

You may interpret and contextualize this data. You must not fabricate new data.

OUTPUT FORMAT: Return a JSON object with the following structure:
{
    "interpretation": "Your analysis text, referencing only provided data",
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "data_references": [
        {"type": "statistic", "key": "possession", "value": "58%"},
        {"type": "event", "key": "goal_23", "value": "Bukayo Saka"},
        {"type": "score", "key": "score_line", "value": "2 - 1"},
        {"type": "team", "key": "home_team", "value": "Arsenal"}
    ]
}

The "data_references" array MUST list every fact you reference in your analysis.
"""

    def build(self, match: Match, metrics: CalculatedMetrics) -> dict:
        return {
            "match": {
                "home_team": {
                    "id": match.home_team.id,
                    "name": match.home_team.name,
                    "short_name": match.home_team.short_name,
                },
                "away_team": {
                    "id": match.away_team.id,
                    "name": match.away_team.name,
                    "short_name": match.away_team.short_name,
                },
                "venue": match.venue,
                "referee": match.referee,
                "status": match.status.value,
                "match_date": match.match_date.isoformat(),
            },
            "calculated_metrics": {
                "score_line": metrics.score_line,
                "match_status_text": metrics.match_status_text,
                "home_score": metrics.home_score,
                "away_score": metrics.away_score,
                "minute": metrics.minute,
                "status": metrics.status,
                "possession_home": metrics.possession_home,
                "possession_away": metrics.possession_away,
                "shots_home": metrics.shots_home,
                "shots_away": metrics.shots_away,
                "shots_on_target_home": metrics.shots_on_target_home,
                "shots_on_target_away": metrics.shots_on_target_away,
                "corners_home": metrics.corners_home,
                "corners_away": metrics.corners_away,
                "recent_events": metrics.recent_events,
                "events_count_home": metrics.events_count_home,
                "events_count_away": metrics.events_count_away,
            },
        }
