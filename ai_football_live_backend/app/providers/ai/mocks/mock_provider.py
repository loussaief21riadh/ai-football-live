import json

from app.providers.ai.base import AIProvider


class MockAIProvider(AIProvider):
    """Mock AI provider that returns deterministic output.

    No external API calls are made.
    Used for development and testing.
    """

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = "json",
        max_tokens: int = 1024,
    ) -> str:
        context = json.loads(user_prompt)
        match = context.get("match", {})
        metrics = context.get("calculated_metrics", {})

        home_team = match.get("home_team", {}).get("name", "Home Team")
        away_team = match.get("away_team", {}).get("name", "Away Team")
        score = metrics.get("score_line", "0 - 0")
        status = metrics.get("status", "unknown")

        if status in ("live", "halftime"):
            interpretation = (
                f"The match between {home_team} and {away_team} is currently "
                f"level at {score}. Both teams have shown attacking intent with "
                f"several chances created. The game remains evenly contested."
            )
            insights = [
                f"Score is currently {score}",
                f"{home_team} has been active in attack",
                f"{away_team} looks dangerous on the counter",
            ]
        elif status == "finished":
            interpretation = (
                f"The match between {home_team} and {away_team} has ended {score}. "
                f"It was an entertaining contest with both teams contributing to the goals."
            )
            insights = [
                f"Final score: {score}",
                "Both teams found the net",
                "An entertaining match for the spectators",
            ]
        else:
            interpretation = (
                f"The upcoming match between {home_team} and {away_team} promises "
                f"to be an interesting contest. Both teams will be looking to secure a win."
            )
            insights = [
                f"Match between {home_team} and {away_team}",
                "Both teams in good form",
                "Expect an entertaining match",
            ]

        output = {
            "interpretation": interpretation,
            "key_insights": insights,
            "data_references": [
                {"type": "score", "key": "score_line", "value": score},
                {"type": "team", "key": "home_team", "value": home_team},
                {"type": "team", "key": "away_team", "value": away_team},
            ],
        }

        return json.dumps(output)

    def get_provider_name(self) -> str:
        return "mock"

    def get_rate_limits(self) -> dict:
        return {"requests_per_minute": None, "tokens_per_day": None}
