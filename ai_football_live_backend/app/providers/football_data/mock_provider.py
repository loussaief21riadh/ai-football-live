from datetime import datetime, timezone, timedelta

from app.providers.football_data.base import FootballDataProvider
from app.core.domain.match import Match, League, Team, MatchEvent, MatchStatistic
from app.core.enums.match_status import MatchStatus, EventType


class MockFootballProvider(FootballDataProvider):
    """Mock football data provider with deterministic data.

    Returns hardcoded, internally consistent match data.
    No external API calls are made.
    """

    def __init__(self):
        self._leagues = self._create_leagues()
        self._teams = self._create_teams()
        self._matches = self._create_matches()
        self._events = self._create_events()
        self._statistics = self._create_statistics()

    def _create_leagues(self) -> list[League]:
        return [
            League(
                id=1,
                provider_name="mock",
                external_id=1001,
                name="Premier League",
                country="England",
                season="2026-2027",
            ),
            League(
                id=2,
                provider_name="mock",
                external_id=1002,
                name="La Liga",
                country="Spain",
                season="2026-2027",
            ),
            League(
                id=3,
                provider_name="mock",
                external_id=1003,
                name="Bundesliga",
                country="Germany",
                season="2026-2027",
            ),
        ]

    def _create_teams(self) -> list[Team]:
        return [
            Team(id=1, provider_name="mock", external_id=101, name="Arsenal", short_name="ARS"),
            Team(id=2, provider_name="mock", external_id=102, name="Chelsea", short_name="CHE"),
            Team(id=3, provider_name="mock", external_id=103, name="Liverpool", short_name="LIV"),
            Team(id=4, provider_name="mock", external_id=104, name="Manchester City", short_name="MCI"),
            Team(id=5, provider_name="mock", external_id=105, name="Barcelona", short_name="BAR"),
            Team(id=6, provider_name="mock", external_id=106, name="Real Madrid", short_name="RMA"),
            Team(id=7, provider_name="mock", external_id=107, name="Bayern Munich", short_name="BAY"),
            Team(id=8, provider_name="mock", external_id=108, name="Borussia Dortmund", short_name="BVB"),
        ]

    def _create_matches(self) -> list[Match]:
        now = datetime.now(timezone.utc)
        leagues = {l.id: l for l in self._leagues}
        teams = {t.id: t for t in self._teams}

        return [
            Match(
                id=1,
                provider_name="mock",
                external_id=2001,
                league=leagues[1],
                home_team=teams[1],
                away_team=teams[2],
                status=MatchStatus.LIVE,
                match_date=now - timedelta(minutes=67),
                venue="Emirates Stadium",
                referee="Michael Oliver",
                minute=67,
                home_score=2,
                away_score=1,
                ht_home_score=1,
                ht_away_score=0,
            ),
            Match(
                id=2,
                provider_name="mock",
                external_id=2002,
                league=leagues[1],
                home_team=teams[3],
                away_team=teams[4],
                status=MatchStatus.SCHEDULED,
                match_date=now + timedelta(hours=2),
                venue="Anfield",
                referee="Anthony Taylor",
            ),
            Match(
                id=3,
                provider_name="mock",
                external_id=2003,
                league=leagues[2],
                home_team=teams[5],
                away_team=teams[6],
                status=MatchStatus.FINISHED,
                match_date=now - timedelta(hours=3),
                venue="Camp Nou",
                referee="Jesus Gil",
                minute=90,
                home_score=3,
                away_score=2,
                ht_home_score=2,
                ht_away_score=1,
            ),
            Match(
                id=4,
                provider_name="mock",
                external_id=2004,
                league=leagues[3],
                home_team=teams[7],
                away_team=teams[8],
                status=MatchStatus.HALFTIME,
                match_date=now - timedelta(minutes=45),
                venue="Allianz Arena",
                referee="Felix Zwayer",
                minute=45,
                home_score=1,
                away_score=1,
                ht_home_score=1,
                ht_away_score=1,
            ),
        ]

    def _create_events(self) -> dict[int, list[MatchEvent]]:
        return {
            1: [
                MatchEvent(
                    id=1,
                    match_id=1,
                    provider_name="mock",
                    external_event_id="evt_101",
                    event_type=EventType.GOAL,
                    minute=23,
                    team_id=1,
                    player_name="Bukayo Saka",
                    assist_player="Martin Odegaard",
                ),
                MatchEvent(
                    id=2,
                    match_id=1,
                    provider_name="mock",
                    external_event_id="evt_102",
                    event_type=EventType.YELLOW_CARD,
                    minute=35,
                    team_id=2,
                    player_name="Enzo Fernandez",
                ),
                MatchEvent(
                    id=3,
                    match_id=1,
                    provider_name="mock",
                    external_event_id="evt_103",
                    event_type=EventType.GOAL,
                    minute=56,
                    team_id=1,
                    player_name="Kai Havertz",
                ),
                MatchEvent(
                    id=4,
                    match_id=1,
                    provider_name="mock",
                    external_event_id="evt_104",
                    event_type=EventType.GOAL,
                    minute=62,
                    team_id=2,
                    player_name="Cole Palmer",
                    assist_player="Noni Madueke",
                ),
            ],
            3: [
                MatchEvent(
                    id=5,
                    match_id=3,
                    provider_name="mock",
                    external_event_id="evt_201",
                    event_type=EventType.GOAL,
                    minute=12,
                    team_id=5,
                    player_name="Robert Lewandowski",
                ),
                MatchEvent(
                    id=6,
                    match_id=3,
                    provider_name="mock",
                    external_event_id="evt_202",
                    event_type=EventType.GOAL,
                    minute=34,
                    team_id=6,
                    player_name="Vinicius Junior",
                ),
                MatchEvent(
                    id=7,
                    match_id=3,
                    provider_name="mock",
                    external_event_id="evt_203",
                    event_type=EventType.GOAL,
                    minute=45,
                    team_id=5,
                    player_name="Lamine Yamal",
                ),
                MatchEvent(
                    id=8,
                    match_id=3,
                    provider_name="mock",
                    external_event_id="evt_204",
                    event_type=EventType.RED_CARD,
                    minute=68,
                    team_id=6,
                    player_name="Jude Bellingham",
                ),
                MatchEvent(
                    id=9,
                    match_id=3,
                    provider_name="mock",
                    external_event_id="evt_205",
                    event_type=EventType.GOAL,
                    minute=78,
                    team_id=5,
                    player_name="Pedri",
                ),
                MatchEvent(
                    id=10,
                    match_id=3,
                    provider_name="mock",
                    external_event_id="evt_206",
                    event_type=EventType.GOAL,
                    minute=85,
                    team_id=6,
                    player_name="Rodrygo",
                ),
            ],
            4: [
                MatchEvent(
                    id=11,
                    match_id=4,
                    provider_name="mock",
                    external_event_id="evt_301",
                    event_type=EventType.GOAL,
                    minute=28,
                    team_id=7,
                    player_name="Harry Kane",
                ),
                MatchEvent(
                    id=12,
                    match_id=4,
                    provider_name="mock",
                    external_event_id="evt_302",
                    event_type=EventType.GOAL,
                    minute=41,
                    team_id=8,
                    player_name="Donyell Malen",
                ),
            ],
        }

    def _create_statistics(self) -> dict[int, list[MatchStatistic]]:
        return {
            1: [
                MatchStatistic(id=1, match_id=1, stat_type="possession", home_value="58", away_value="42"),
                MatchStatistic(id=2, match_id=1, stat_type="shots", home_value="12", away_value="8"),
                MatchStatistic(id=3, match_id=1, stat_type="shots_on_target", home_value="6", away_value="3"),
                MatchStatistic(id=4, match_id=1, stat_type="corners", home_value="7", away_value="4"),
                MatchStatistic(id=5, match_id=1, stat_type="fouls", home_value="8", away_value="11"),
            ],
            3: [
                MatchStatistic(id=6, match_id=3, stat_type="possession", home_value="62", away_value="38"),
                MatchStatistic(id=7, match_id=3, stat_type="shots", home_value="15", away_value="10"),
                MatchStatistic(id=8, match_id=3, stat_type="shots_on_target", home_value="8", away_value="5"),
                MatchStatistic(id=9, match_id=3, stat_type="corners", home_value="9", away_value="5"),
            ],
            4: [
                MatchStatistic(id=10, match_id=4, stat_type="possession", home_value="55", away_value="45"),
                MatchStatistic(id=11, match_id=4, stat_type="shots", home_value="10", away_value="7"),
                MatchStatistic(id=12, match_id=4, stat_type="shots_on_target", home_value="4", away_value="3"),
            ],
        }

    async def get_live_matches(self) -> list[Match]:
        return [m for m in self._matches if m.status in (MatchStatus.LIVE, MatchStatus.HALFTIME)]

    async def get_upcoming_matches(self, hours: int = 24) -> list[Match]:
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(hours=hours)
        return [
            m for m in self._matches
            if m.status == MatchStatus.SCHEDULED and m.match_date <= cutoff
        ]

    async def get_match_by_internal_id(self, match_id: int) -> Match | None:
        for match in self._matches:
            if match.id == match_id:
                match.events = self._events.get(match_id, [])
                match.statistics = self._statistics.get(match_id, [])
                return match
        return None

    async def get_match_events(self, match_id: int) -> list[MatchEvent]:
        return self._events.get(match_id, [])

    async def get_match_statistics(self, match_id: int) -> list[MatchStatistic]:
        return self._statistics.get(match_id, [])

    async def get_leagues(self) -> list[League]:
        return self._leagues
