import json
import re
from dataclasses import dataclass

from app.core.domain.match import Match
from app.core.domain.analysis import CalculatedMetrics


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


class AIOutputValidator:
    """Validates LLM output against source data to prevent hallucination."""

    def validate_structure(self, raw_json: str) -> tuple[dict | None, str | None]:
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON: {e}"

        required_fields = ["interpretation", "key_insights", "data_references"]
        for field in required_fields:
            if field not in data:
                return None, f"Missing required field: {field}"

        if not isinstance(data["interpretation"], str) or len(data["interpretation"]) < 10:
            return None, "Interpretation must be a string with at least 10 characters"

        if not isinstance(data["key_insights"], list) or len(data["key_insights"]) == 0:
            return None, "key_insights must be a non-empty array"

        if not isinstance(data["data_references"], list):
            return None, "data_references must be an array"

        return data, None

    def validate_against_source(
        self,
        output: dict,
        match: Match,
        metrics: CalculatedMetrics,
    ) -> ValidationResult:
        errors = []

        source_score = f"{match.home_score} - {match.away_score}"
        valid_scores = {source_score}
        if match.ht_home_score is not None and match.ht_away_score is not None:
            ht_score = f"{match.ht_home_score} - {match.ht_away_score}"
            valid_scores.add(ht_score)

        teams = {
            match.home_team.name,
            match.home_team.short_name,
            match.away_team.name,
            match.away_team.short_name,
        }

        known_stats = {}
        for stat in match.statistics:
            known_stats[stat.stat_type] = f"{stat.home_value} - {stat.away_value}"
            known_stats[f"{stat.stat_type}_home"] = stat.home_value
            known_stats[f"{stat.stat_type}_away"] = stat.away_value

        for ref in output.get("data_references", []):
            ref_type = ref.get("type")
            ref_key = ref.get("key")
            ref_value = ref.get("value")

            if ref_type == "score":
                if ref_value not in valid_scores:
                    errors.append(f"Score mismatch: '{ref_value}' not in source {valid_scores}")

            elif ref_type == "team":
                if ref_value not in teams:
                    errors.append(f"Unknown team: '{ref_value}'")

            elif ref_type == "statistic":
                if ref_key not in known_stats:
                    errors.append(f"Hallucinated stat key: '{ref_key}'")
                elif ref_value != known_stats[ref_key]:
                    errors.append(
                        f"Stat value mismatch for '{ref_key}': "
                        f"LLM said '{ref_value}', source says '{known_stats[ref_key]}'"
                    )

            elif ref_type == "event":
                pass

        interpretation = output.get("interpretation", "")
        score_pattern = r"\b(\d{1,2})\s*[-:]\s*(\d{1,2})\b"
        for home_str, away_str in re.findall(score_pattern, interpretation):
            found = f"{home_str} - {away_str}"
            if found not in valid_scores:
                errors.append(f"Score '{found}' in interpretation not in source data")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def compute_reference_validation_rate(
        self,
        output: dict,
        match: Match,
    ) -> tuple[float, str]:
        refs = output.get("data_references", [])
        if not refs:
            return 0.0, "low"

        valid_count = 0
        teams = {
            match.home_team.name,
            match.home_team.short_name,
            match.away_team.name,
            match.away_team.short_name,
        }
        source_score = f"{match.home_score} - {match.away_score}"

        for ref in refs:
            ref_type = ref.get("type")
            ref_value = ref.get("value")

            if ref_type == "score" and ref_value == source_score:
                valid_count += 1
            elif ref_type == "team" and ref_value in teams:
                valid_count += 1
            elif ref_type == "statistic":
                valid_count += 1

        rate = valid_count / len(refs)
        if rate >= 0.9:
            label = "high"
        elif rate >= 0.5:
            label = "partial"
        else:
            label = "low"

        return rate, label
