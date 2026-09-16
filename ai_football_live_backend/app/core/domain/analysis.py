from dataclasses import dataclass


@dataclass
class CalculatedMetrics:
    """Factual metrics derived from provider data.

    All values in this class are either:
    (a) directly from the football provider, or
    (b) simple formatting/derivation of provider data.

    None of these are heuristic estimates or invented statistics.
    """

    score_line: str
    match_status_text: str
    home_score: int
    away_score: int
    minute: int | None
    status: str

    possession_home: float | None = None
    possession_away: float | None = None
    shots_home: int | None = None
    shots_away: int | None = None
    shots_on_target_home: int | None = None
    shots_on_target_away: int | None = None
    corners_home: int | None = None
    corners_away: int | None = None

    recent_events: list[str] = None
    events_count_home: int = 0
    events_count_away: int = 0

    def __post_init__(self):
        if self.recent_events is None:
            self.recent_events = []
