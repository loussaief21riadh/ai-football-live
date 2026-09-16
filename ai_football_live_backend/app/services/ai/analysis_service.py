import json
import hashlib
from datetime import datetime, timezone

from app.providers.ai.base import AIProvider
from app.services.ai.deterministic_engine import DeterministicAnalysisEngine
from app.services.ai.context_builder import AIContextBuilder
from app.services.ai.output_validator import AIOutputValidator
from app.core.domain.match import Match
from app.core.domain.match import AIAnalysis


class AnalysisService:
    """Orchestrates the AI analysis pipeline.

    Pipeline:
    1. DeterministicAnalysisEngine computes factual metrics
    2. AIContextBuilder assembles context for LLM
    3. AIProvider generates interpretation
    4. OutputValidator validates against source data
    5. Returns validated analysis or None if validation fails
    """

    def __init__(self, ai_provider: AIProvider):
        self._ai_provider = ai_provider
        self._engine = DeterministicAnalysisEngine()
        self._context_builder = AIContextBuilder()
        self._validator = AIOutputValidator()

    async def generate_analysis(
        self,
        match: Match,
        analysis_type: str,
    ) -> AIAnalysis | None:
        metrics = self._engine.calculate(match)
        context = self._context_builder.build(match, metrics)
        system_prompt = self._context_builder.build_system_prompt()

        try:
            raw_output = await self._ai_provider.generate(
                system_prompt=system_prompt,
                user_prompt=json.dumps(context),
                response_format="json",
            )
        except Exception:
            return None

        parsed, error = self._validator.validate_structure(raw_output)
        if error:
            return None

        result = self._validator.validate_against_source(parsed, match, metrics)
        if not result.is_valid:
            return None

        validation_rate, validation_label = self._validator.compute_reference_validation_rate(
            parsed, match
        )

        context_fingerprint = hashlib.sha256(
            json.dumps(context, sort_keys=True).encode()
        ).hexdigest()

        return AIAnalysis(
            id=None,
            match_id=match.id or 0,
            analysis_type=analysis_type,
            context_fingerprint=context_fingerprint,
            interpretation=parsed["interpretation"],
            key_insights=parsed["key_insights"],
            reference_validation_rate=validation_rate,
            validation_label=validation_label,
            data_references=parsed["data_references"],
            validation_result="passed",
            ai_provider=self._ai_provider.get_provider_name(),
            generated_at=datetime.now(timezone.utc),
        )
