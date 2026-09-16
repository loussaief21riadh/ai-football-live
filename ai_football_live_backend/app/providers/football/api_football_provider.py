import logging
from datetime import datetime, timezone

import httpx

from app.providers.football_data.base import FootballDataProvider
from app.core.domain.match import Match, League, Team, MatchEvent, MatchStatistic
from app.core.enums.match_status import MatchStatus, EventType
from app.providers.football.errors import (
    FootballProviderConfigurationError,
    FootballProviderAuthenticationError,
    FootballProviderRateLimitError,
    FootballProviderTimeoutError,
    FootballProviderNetworkError,
    FootballProviderResponseError,
)

logger = logging.getLogger(__name__)

PROVIDER_NAME = "api-football"

STATUS_MAP: dict[str, MatchStatus] = {
    "TBD": MatchStatus.SCHEDULED,
    "NS": MatchStatus.SCHEDULED,
    "1H": MatchStatus.LIVE,
    "HT": MatchStatus.HALFTIME,
    "2H": MatchStatus.LIVE,
    "ET": MatchStatus.LIVE,
    "BT": MatchStatus.LIVE,
    "P": MatchStatus.LIVE,
    "FT": MatchStatus.FINISHED,
    "AET": MatchStatus.FINISHED,
    "PEN": MatchStatus.FINISHED,
    "PST": MatchStatus.POSTPONED,
    "CANC": MatchStatus.CANCELLED,
    "ABD": MatchStatus.CANCELLED,
    "SUSP": MatchStatus.POSTPONED,
    "INT": MatchStatus.POSTPONED,
    "PRT": MatchStatus.LIVE,
    "LIVE": MatchStatus.LIVE,
}

EVENT_TYPE_MAP: dict[str, EventType] = {
    "Goal": EventType.GOAL,
    "Normal Goal": EventType.GOAL,
    "Own Goal": EventType.OWN_GOAL,
    "Penalty": EventType.PENALTY_SCORED,
    "Missed Penalty": EventType.PENALTY_MISSED,
    "Card": EventType.YELLOW_CARD,
    "Yellow Card": EventType.YELLOW_CARD,
    "Red Card": EventType.RED_CARD,
    "Yellow-Red Card": EventType.RED_CARD,
    "subst": EventType.SUBSTITUTION,
    "Substitution": EventType.SUBSTITUTION,
    "Var": EventType.VAR_DECISION,
    "VAR": EventType.VAR_DECISION,
}


def _parse_elapsed(elapsed: int | str | None) -> int | None:
    if elapsed is None:
        return None
    try:
        return int(elapsed)
    except (ValueError, TypeError):
        return None


def _safe_int(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _safe_str(value) -> str | None:
    if value is None:
        return None
    return str(value).strip() or None


class ApiFootballProvider(FootballDataProvider):
    """Real football data provider using API-Football v3."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://v3.football.api-sports.io",
        timeout: int = 10,
        league_ids: list[int] | None = None,
        season: int | None = None,
    ):
        if not api_key:
            raise FootballProviderConfigurationError(
                "FOOTBALL_API_KEY is required for ApiFootballProvider. "
                "Set FOOTBALL_PROVIDER=mock for local development without an API key."
            )
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._league_ids = league_ids
        self._season = season

    def _get_headers(self) -> dict[str, str]:
        return {
            "x-apisports-key": self._api_key,
            "Accept": "application/json",
        }

    async def _request(self, path: str, params: dict | None = None) -> dict:
        url = f"{self._base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    url, headers=self._get_headers(), params=params
                )
        except httpx.TimeoutException as e:
            raise FootballProviderTimeoutError(
                f"API-Football request timed out after {self._timeout}s"
            ) from e
        except httpx.ConnectError as e:
            raise FootballProviderNetworkError(
                "Failed to connect to API-Football"
            ) from e
        except httpx.RequestError as e:
            raise FootballProviderNetworkError(
                f"API-Football request failed: {type(e).__name__}"
            ) from e

        if response.status_code == 401 or response.status_code == 403:
            raise FootballProviderAuthenticationError(
                "Invalid or missing API-Football key"
            )

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_int = _safe_int(retry_after) if retry_after else None
            raise FootballProviderRateLimitError(
                "API-Football rate limit exceeded",
                retry_after=retry_after_int,
            )

        if response.status_code >= 400:
            raise FootballProviderResponseError(
                f"API-Football HTTP {response.status_code}"
            )

        try:
            data = response.json()
        except Exception as e:
            raise FootballProviderResponseError(
                "API-Football returned invalid JSON"
            ) from e

        errors = data.get("errors", {})
        if errors:
            error_msg = ", ".join(f"{k}: {v}" for k, v in errors.items())
            error_keys_lower = {k.lower() for k in errors}
            if "token" in error_keys_lower or "key" in error_keys_lower:
                raise FootballProviderAuthenticationError(
                    "API-Football authentication error"
                )
            if "ratelimit" in error_keys_lower:
                raise FootballProviderRateLimitError(
                    "API-Football rate limit exceeded"
                )
            raise FootballProviderResponseError(
                f"API-Football API error: {error_msg}"
            )

        return data

    def _parse_league(self, league_data: dict, country_data: dict | None = None) -> League:
        league_info = league_data if "id" in league_data else {}
        return League(
            id=None,
            provider_name=PROVIDER_NAME,
            external_id=league_info.get("id", 0),
            name=league_info.get("name", "Unknown"),
            country=_safe_str((country_data or {}).get("name")),
            logo_url=_safe_str(league_info.get("logo")),
            season=_safe_str(self._season) if self._season else None,
        )

    def _parse_team(self, team_data: dict) -> Team:
        return Team(
            id=None,
            provider_name=PROVIDER_NAME,
            external_id=team_data.get("id", 0),
            name=team_data.get("name", "Unknown"),
            short_name=_safe_str(team_data.get("logo")),
            logo_url=_safe_str(team_data.get("logo")),
        )

    def _parse_fixture(self, fixture_data: dict) -> Match:
        fixture = fixture_data.get("fixture", {})
        league = fixture_data.get("league", {})
        teams = fixture_data.get("teams", {})
        goals = fixture_data.get("goals", {})
        score = fixture_data.get("score", {})

        status_code = fixture.get("status", {}).get("short", "NS")
        status = STATUS_MAP.get(status_code, MatchStatus.UNKNOWN)

        match_date_str = fixture.get("date", "")
        match_date = datetime.now(timezone.utc)
        if match_date_str:
            try:
                match_date = datetime.fromisoformat(
                    match_date_str.replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                match_date = datetime.now(timezone.utc)

        elapsed = _parse_elapsed(fixture.get("status", {}).get("elapsed"))

        ht = score.get("halftime", {})

        return Match(
            id=None,
            provider_name=PROVIDER_NAME,
            external_id=fixture.get("id", 0),
            league=self._parse_league(league, None),
            home_team=self._parse_team(teams.get("home", {})),
            away_team=self._parse_team(teams.get("away", {})),
            status=status,
            match_date=match_date,
            venue=_safe_str(fixture.get("venue", {}).get("name")),
            referee=_safe_str(fixture.get("referee")),
            minute=elapsed,
            home_score=_safe_int(goals.get("home")) or 0,
            away_score=_safe_int(goals.get("away")) or 0,
            ht_home_score=_safe_int(ht.get("home")),
            ht_away_score=_safe_int(ht.get("away")),
        )

    async def get_live_matches(self) -> list[Match]:
        data = await self._request("/fixtures", {"live": "all"})
        response = data.get("response", [])
        matches = [self._parse_fixture(f) for f in response]
        if self._league_ids:
            matches = [m for m in matches if m.league.external_id in self._league_ids]
        return matches

    async def get_upcoming_matches(self, hours: int = 24) -> list[Match]:
        now = datetime.now(timezone.utc)
        params: dict = {}
        if self._league_ids:
            params["league"] = ",".join(str(lid) for lid in self._league_ids)
        if self._season:
            params["season"] = self._season
        params["next"] = hours

        data = await self._request("/fixtures", params)
        response = data.get("response", [])
        matches = [self._parse_fixture(f) for f in response]
        return matches

    async def get_match_by_internal_id(self, match_id: int) -> Match | None:
        data = await self._request("/fixtures", {"id": match_id})
        response = data.get("response", [])
        if not response:
            return None
        return self._parse_fixture(response[0])

    async def get_match_events(self, match_id: int) -> list[MatchEvent]:
        data = await self._request("/fixtures/events", {"fixture": match_id})
        response = data.get("response", [])

        events = []
        for event in response:
            time_data = event.get("time", {})
            minute = _parse_elapsed(time_data.get("elapsed")) or 0
            extra = _parse_elapsed(time_data.get("extra"))

            event_type_str = event.get("type", "")
            detail_str = event.get("detail", "")
            event_type = EVENT_TYPE_MAP.get(
                detail_str, EVENT_TYPE_MAP.get(event_type_str, EventType.UNKNOWN)
            )

            team_data = event.get("team", {})
            player_data = event.get("player", {})
            assist_data = event.get("assist", {})

            events.append(MatchEvent(
                id=None,
                match_id=match_id,
                provider_name=PROVIDER_NAME,
                external_event_id=_safe_str(event.get("id")),
                event_type=event_type,
                minute=minute,
                added_time=extra,
                team_id=_safe_int(team_data.get("id")),
                player_name=_safe_str(player_data.get("name")),
                assist_player=_safe_str(assist_data.get("name")),
                detail=_safe_str(detail_str),
            ))

        return events

    async def get_match_statistics(self, match_id: int) -> list[MatchStatistic]:
        data = await self._request("/fixtures/statistics", {"fixture": match_id})
        response = data.get("response", [])

        stats: list[MatchStatistic] = []

        for idx, team_stat in enumerate(response):
            is_home = idx == 0
            values = team_stat.get("statistics", [])

            for stat_entry in values:
                stat_type = stat_entry.get("type", "")
                value = stat_entry.get("value")
                value_str = str(value) if value is not None else None

                existing = next((s for s in stats if s.stat_type == stat_type), None)
                if existing:
                    if not is_home:
                        existing.away_value = value_str
                else:
                    stat = MatchStatistic(
                        id=None,
                        match_id=match_id,
                        stat_type=stat_type,
                        home_value=value_str if is_home else None,
                        away_value=value_str if not is_home else None,
                    )
                    stats.append(stat)

        return stats

    async def get_leagues(self) -> list[League]:
        params: dict = {}
        if self._league_ids:
            params["id"] = ",".join(str(lid) for lid in self._league_ids)

        data = await self._request("/leagues", params)
        response = data.get("response", [])

        leagues = []
        for league_data in response:
            league_info = league_data.get("league", {})
            country_info = league_data.get("country", {})
            leagues.append(League(
                id=None,
                provider_name=PROVIDER_NAME,
                external_id=league_info.get("id", 0),
                name=league_info.get("name", "Unknown"),
                country=_safe_str(country_info.get("name")),
                logo_url=_safe_str(league_info.get("logo")),
                season=_safe_str(self._season) if self._season else None,
            ))

        return leagues
