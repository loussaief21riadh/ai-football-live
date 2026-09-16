import 'enums.dart';

class LeagueModel {
  final int id;
  final String providerName;
  final int externalId;
  final String name;
  final String? country;
  final String? logoUrl;
  final String? season;

  const LeagueModel({
    required this.id,
    required this.providerName,
    required this.externalId,
    required this.name,
    this.country,
    this.logoUrl,
    this.season,
  });

  factory LeagueModel.fromJson(Map<String, dynamic> json) {
    return LeagueModel(
      id: json['id'] as int? ?? 0,
      providerName: json['provider_name'] as String? ?? '',
      externalId: json['external_id'] as int? ?? 0,
      name: json['name'] as String? ?? '',
      country: json['country'] as String?,
      logoUrl: json['logo_url'] as String?,
      season: json['season'] as String?,
    );
  }
}

class TeamModel {
  final int id;
  final String providerName;
  final int externalId;
  final String name;
  final String? shortName;
  final String? logoUrl;

  const TeamModel({
    required this.id,
    required this.providerName,
    required this.externalId,
    required this.name,
    this.shortName,
    this.logoUrl,
  });

  factory TeamModel.fromJson(Map<String, dynamic> json) {
    return TeamModel(
      id: json['id'] as int? ?? 0,
      providerName: json['provider_name'] as String? ?? '',
      externalId: json['external_id'] as int? ?? 0,
      name: json['name'] as String? ?? '',
      shortName: json['short_name'] as String?,
      logoUrl: json['logo_url'] as String?,
    );
  }
}

class MatchEventModel {
  final int id;
  final EventType eventType;
  final int minute;
  final int? addedTime;
  final String? playerName;
  final String? assistPlayer;
  final int? teamId;
  final String? detail;

  const MatchEventModel({
    required this.id,
    required this.eventType,
    required this.minute,
    this.addedTime,
    this.playerName,
    this.assistPlayer,
    this.teamId,
    this.detail,
  });

  factory MatchEventModel.fromJson(Map<String, dynamic> json) {
    final rawId = json['id'];
    final int id;
    if (rawId is int) {
      id = rawId;
    } else if (rawId is num) {
      id = rawId.toInt();
    } else {
      id = 0;
    }

    return MatchEventModel(
      id: id,
      eventType: EventType.fromString(json['event_type'] as String?),
      minute: json['minute'] as int? ?? 0,
      addedTime: json['added_time'] as int?,
      playerName: json['player_name'] as String?,
      assistPlayer: json['assist_player'] as String?,
      teamId: json['team_id'] as int?,
      detail: json['detail'] as String?,
    );
  }
}

class MatchStatisticModel {
  final int id;
  final String statType;
  final String? homeValue;
  final String? awayValue;

  const MatchStatisticModel({
    required this.id,
    required this.statType,
    this.homeValue,
    this.awayValue,
  });

  factory MatchStatisticModel.fromJson(Map<String, dynamic> json) {
    final rawId = json['id'];
    final int id;
    if (rawId is int) {
      id = rawId;
    } else if (rawId is num) {
      id = rawId.toInt();
    } else {
      id = 0;
    }

    return MatchStatisticModel(
      id: id,
      statType: json['stat_type'] as String? ?? '',
      homeValue: json['home_value'] as String?,
      awayValue: json['away_value'] as String?,
    );
  }
}

class MatchModel {
  final int id;
  final String providerName;
  final int externalId;
  final LeagueModel league;
  final TeamModel homeTeam;
  final TeamModel awayTeam;
  final MatchStatus status;
  final int? minute;
  final int? addedTime;
  final int homeScore;
  final int awayScore;
  final int? htHomeScore;
  final int? htAwayScore;
  final DateTime matchDate;
  final String? venue;
  final String? referee;
  final List<MatchEventModel> events;
  final List<MatchStatisticModel> statistics;

  const MatchModel({
    required this.id,
    required this.providerName,
    required this.externalId,
    required this.league,
    required this.homeTeam,
    required this.awayTeam,
    required this.status,
    this.minute,
    this.addedTime,
    required this.homeScore,
    required this.awayScore,
    this.htHomeScore,
    this.htAwayScore,
    required this.matchDate,
    this.venue,
    this.referee,
    this.events = const [],
    this.statistics = const [],
  });

  factory MatchModel.fromJson(Map<String, dynamic> json) {
    final id = json['id'];
    if (id == null || id is! int) {
      throw const FormatException('Match missing required field: id (expected int)');
    }

    final leagueData = json['league'];
    if (leagueData == null || leagueData is! Map<String, dynamic>) {
      throw const FormatException('Match missing required field: league (expected Map)');
    }

    final homeTeamData = json['home_team'];
    if (homeTeamData == null || homeTeamData is! Map<String, dynamic>) {
      throw const FormatException('Match missing required field: home_team (expected Map)');
    }

    final awayTeamData = json['away_team'];
    if (awayTeamData == null || awayTeamData is! Map<String, dynamic>) {
      throw const FormatException('Match missing required field: away_team (expected Map)');
    }

    final matchDateStr = json['match_date'];
    if (matchDateStr == null || matchDateStr is! String) {
      throw const FormatException('Match missing required field: match_date (expected String)');
    }

    final DateTime matchDate;
    try {
      matchDate = DateTime.parse(matchDateStr);
    } catch (_) {
      throw FormatException('Match has invalid match_date: $matchDateStr');
    }

    return MatchModel(
      id: id,
      providerName: json['provider_name'] as String? ?? '',
      externalId: json['external_id'] as int? ?? 0,
      league: LeagueModel.fromJson(leagueData),
      homeTeam: TeamModel.fromJson(homeTeamData),
      awayTeam: TeamModel.fromJson(awayTeamData),
      status: MatchStatus.fromString(json['status'] as String?),
      minute: json['minute'] as int?,
      addedTime: json['added_time'] as int?,
      homeScore: json['home_score'] as int? ?? 0,
      awayScore: json['away_score'] as int? ?? 0,
      htHomeScore: json['ht_home_score'] as int?,
      htAwayScore: json['ht_away_score'] as int?,
      matchDate: matchDate,
      venue: json['venue'] as String?,
      referee: json['referee'] as String?,
      events: (json['events'] as List<dynamic>?)
          ?.map((e) => MatchEventModel.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
      statistics: (json['statistics'] as List<dynamic>?)
          ?.map((s) => MatchStatisticModel.fromJson(s as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  String get scoreLine => '$homeScore - $awayScore';

  String get statusText {
    switch (status) {
      case MatchStatus.finished:
        return 'Full Time';
      case MatchStatus.halftime:
        return 'Half Time';
      case MatchStatus.live:
        if (minute != null) {
          if (addedTime != null) {
            return "$minute+$addedTime'";
          }
          return "$minute'";
        }
        return 'Live';
      case MatchStatus.scheduled:
        return '${matchDate.hour.toString().padLeft(2, '0')}:${matchDate.minute.toString().padLeft(2, '0')}';
      default:
        return status.value;
    }
  }
}

class AIAnalysisModel {
  final int? id;
  final int matchId;
  final String analysisType;
  final String interpretation;
  final List<String> keyInsights;
  final double referenceValidationRate;
  final String validationLabel;
  final List<Map<String, dynamic>> dataReferences;
  final String validationResult;
  final String aiProvider;
  final DateTime generatedAt;

  const AIAnalysisModel({
    this.id,
    required this.matchId,
    required this.analysisType,
    required this.interpretation,
    required this.keyInsights,
    required this.referenceValidationRate,
    required this.validationLabel,
    required this.dataReferences,
    required this.validationResult,
    required this.aiProvider,
    required this.generatedAt,
  });

  factory AIAnalysisModel.fromJson(Map<String, dynamic> json) {
    final generatedAtStr = json['generated_at'];
    final DateTime generatedAt;
    if (generatedAtStr != null && generatedAtStr is String) {
      try {
        generatedAt = DateTime.parse(generatedAtStr);
      } catch (_) {
        throw FormatException('AIAnalysis has invalid generated_at: $generatedAtStr');
      }
    } else {
      throw const FormatException('AIAnalysis missing required field: generated_at');
    }

    return AIAnalysisModel(
      id: json['id'] as int?,
      matchId: json['match_id'] as int,
      analysisType: json['analysis_type'] as String? ?? '',
      interpretation: json['interpretation'] as String? ?? '',
      keyInsights: List<String>.from(json['key_insights'] as List? ?? []),
      referenceValidationRate: (json['reference_validation_rate'] as num?)?.toDouble() ?? 0.0,
      validationLabel: json['validation_label'] as String? ?? 'low',
      dataReferences: List<Map<String, dynamic>>.from(json['data_references'] as List? ?? []),
      validationResult: json['validation_result'] as String? ?? 'pending',
      aiProvider: json['ai_provider'] as String? ?? 'unknown',
      generatedAt: generatedAt,
    );
  }
}

class StreamInfoModel {
  final bool available;
  final String? embedUrl;
  final String? providerName;
  final String? quality;
  final String? language;
  final String message;
  final int alternatives;

  const StreamInfoModel({
    required this.available,
    this.embedUrl,
    this.providerName,
    this.quality,
    this.language,
    required this.message,
    required this.alternatives,
  });

  factory StreamInfoModel.fromJson(Map<String, dynamic> json) {
    final streamData = json['stream'];
    final Map<String, dynamic>? stream;
    if (streamData == null) {
      stream = null;
    } else if (streamData is Map<String, dynamic>) {
      stream = streamData;
    } else {
      stream = null;
    }

    return StreamInfoModel(
      available: json['available'] as bool? ?? false,
      embedUrl: stream?['embed_url'] as String?,
      providerName: stream?['provider_name'] as String?,
      quality: stream?['quality'] as String?,
      language: stream?['language'] as String?,
      message: json['message'] as String? ?? '',
      alternatives: json['alternatives'] as int? ?? 0,
    );
  }
}
