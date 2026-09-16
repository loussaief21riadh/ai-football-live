enum MatchStatus {
  scheduled('scheduled'),
  timeline('timeline'),
  live('live'),
  halftime('halftime'),
  finished('finished'),
  postponed('postponed'),
  cancelled('cancelled'),
  unknown('unknown');

  final String value;
  const MatchStatus(this.value);

  factory MatchStatus.fromString(String? value) {
    if (value == null) return MatchStatus.unknown;
    return MatchStatus.values.firstWhere(
      (s) => s.value == value,
      orElse: () => MatchStatus.unknown,
    );
  }

  bool get isLive => this == MatchStatus.live || this == MatchStatus.halftime;
  bool get isFinished => this == MatchStatus.finished;
  bool get isScheduled => this == MatchStatus.scheduled;
}

enum EventType {
  goal('goal'),
  ownGoal('own_goal'),
  penaltyScored('penalty_scored'),
  penaltyMissed('penalty_missed'),
  yellowCard('yellow_card'),
  redCard('red_card'),
  substitution('substitution'),
  varDecision('var_decision'),
  injury('injury'),
  unknown('unknown');

  final String value;
  const EventType(this.value);

  factory EventType.fromString(String? value) {
    if (value == null) return EventType.unknown;
    return EventType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => EventType.unknown,
    );
  }
}

enum AnalysisType {
  preMatch('pre_match'),
  live('live'),
  postMatch('post_match'),
  unknown('unknown');

  final String value;
  const AnalysisType(this.value);

  factory AnalysisType.fromString(String? value) {
    if (value == null) return AnalysisType.unknown;
    return AnalysisType.values.firstWhere(
      (a) => a.value == value,
      orElse: () => AnalysisType.unknown,
    );
  }
}

enum StreamAuthorizationStatus {
  authorized('authorized'),
  unavailable('unavailable'),
  pending('pending'),
  unknown('unknown');

  final String value;
  const StreamAuthorizationStatus(this.value);

  factory StreamAuthorizationStatus.fromString(String? value) {
    if (value == null) return StreamAuthorizationStatus.unknown;
    return StreamAuthorizationStatus.values.firstWhere(
      (s) => s.value == value,
      orElse: () => StreamAuthorizationStatus.unknown,
    );
  }
}
