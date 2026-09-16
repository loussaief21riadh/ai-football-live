import json
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.ai.analysis_service import AnalysisService
from app.providers.ai.groq_provider import GroqAIProvider
from app.providers.ai.errors import AIProviderUnavailableError
from app.core.domain.match import Match, League, Team, MatchStatistic
from app.core.enums.match_status import MatchStatus


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
        status=MatchStatus.LIVE,
        match_date=datetime(2026, 9, 15, 19, 0, 0, tzinfo=timezone.utc),
        minute=67, home_score=2, away_score=1,
        statistics=statistics,
    )


class TestAnalysisWithMockedGroq:
    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_full_pipeline_with_groq(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3

        groq_response = json.dumps({
            "interpretation": "The match between Arsenal and Chelsea is currently level at 2 - 1.",
            "key_insights": [
                "Score is currently 2 - 1",
                "Arsenal leads with strong attacking play",
            ],
            "data_references": [
                {"type": "score", "key": "score_line", "value": "2 - 1"},
                {"type": "team", "key": "home_team", "value": "Arsenal"},
                {"type": "team", "key": "away_team", "value": "Chelsea"},
            ],
        })

        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(choices=[MagicMock(message=MagicMock(content=groq_response))])
        )

        provider = GroqAIProvider()
        service = AnalysisService(provider)
        match = create_test_match()
        result = await service.generate_analysis(match, "live")

        assert result is not None
        assert result.ai_provider == "groq"
        assert result.analysis_type == "live"
        assert "Arsenal" in result.interpretation
        assert result.reference_validation_rate == 1.0

    @patch("app.providers.ai.groq_provider.settings")
    @patch("groq.AsyncGroq")
    @pytest.mark.asyncio
    async def test_hallucinated_output_rejected(self, mock_cls, mock_settings):
        mock_settings.ai.GROQ_API_KEY = "test-key"
        mock_settings.ai.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.ai.AI_TIMEOUT_SECONDS = 30
        mock_settings.ai.AI_TEMPERATURE = 0.3

        groq_response = json.dumps({
            "interpretation": "The match is currently 0 - 0 with total dominance.",
            "key_insights": ["Score is 0 - 0"],
            "data_references": [
                {"type": "score", "key": "score_line", "value": "0 - 0"},
            ],
        })

        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(choices=[MagicMock(message=MagicMock(content=groq_response))])
        )

        provider = GroqAIProvider()
        service = AnalysisService(provider)
        match = create_test_match()
        result = await service.generate_analysis(match, "live")

        assert result is None

    @pytest.mark.asyncio
    async def test_provider_unavailable_returns_none(self):
        provider = AsyncMock()
        provider.generate = AsyncMock(side_effect=AIProviderUnavailableError("down"))
        service = AnalysisService(provider)
        match = create_test_match()
        result = await service.generate_analysis(match, "live")
        assert result is None
