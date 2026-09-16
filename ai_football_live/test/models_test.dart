import 'package:flutter_test/flutter_test.dart';
import 'package:ai_football_live/models/enums.dart';
import 'package:ai_football_live/models/models.dart';

void main() {
  group('MatchStatus', () {
    test('fromString returns correct status', () {
      expect(MatchStatus.fromString('live'), MatchStatus.live);
      expect(MatchStatus.fromString('scheduled'), MatchStatus.scheduled);
      expect(MatchStatus.fromString('finished'), MatchStatus.finished);
      expect(MatchStatus.fromString('halftime'), MatchStatus.halftime);
      expect(MatchStatus.fromString('postponed'), MatchStatus.postponed);
      expect(MatchStatus.fromString('cancelled'), MatchStatus.cancelled);
      expect(MatchStatus.fromString('timeline'), MatchStatus.timeline);
    });

    test('fromString returns unknown for null', () {
      expect(MatchStatus.fromString(null), MatchStatus.unknown);
    });

    test('fromString returns unknown for invalid value', () {
      expect(MatchStatus.fromString('invalid'), MatchStatus.unknown);
    });

    test('isLive returns true for live and halftime', () {
      expect(MatchStatus.live.isLive, true);
      expect(MatchStatus.halftime.isLive, true);
      expect(MatchStatus.finished.isLive, false);
      expect(MatchStatus.scheduled.isLive, false);
    });

    test('isFinished returns true only for finished', () {
      expect(MatchStatus.finished.isFinished, true);
      expect(MatchStatus.live.isFinished, false);
      expect(MatchStatus.scheduled.isFinished, false);
    });

    test('isScheduled returns true only for scheduled', () {
      expect(MatchStatus.scheduled.isScheduled, true);
      expect(MatchStatus.live.isScheduled, false);
      expect(MatchStatus.finished.isScheduled, false);
    });
  });

  group('EventType', () {
    test('fromString returns correct type', () {
      expect(EventType.fromString('goal'), EventType.goal);
      expect(EventType.fromString('yellow_card'), EventType.yellowCard);
      expect(EventType.fromString('red_card'), EventType.redCard);
      expect(EventType.fromString('own_goal'), EventType.ownGoal);
      expect(EventType.fromString('penalty_scored'), EventType.penaltyScored);
      expect(EventType.fromString('penalty_missed'), EventType.penaltyMissed);
      expect(EventType.fromString('substitution'), EventType.substitution);
      expect(EventType.fromString('var_decision'), EventType.varDecision);
      expect(EventType.fromString('injury'), EventType.injury);
    });

    test('fromString returns unknown for null', () {
      expect(EventType.fromString(null), EventType.unknown);
    });

    test('fromString returns unknown for invalid value', () {
      expect(EventType.fromString('invalid'), EventType.unknown);
    });
  });

  group('AnalysisType', () {
    test('fromString returns correct type', () {
      expect(AnalysisType.fromString('pre_match'), AnalysisType.preMatch);
      expect(AnalysisType.fromString('live'), AnalysisType.live);
      expect(AnalysisType.fromString('post_match'), AnalysisType.postMatch);
    });

    test('fromString returns unknown for null', () {
      expect(AnalysisType.fromString(null), AnalysisType.unknown);
    });
  });

  group('StreamAuthorizationStatus', () {
    test('fromString returns correct status', () {
      expect(StreamAuthorizationStatus.fromString('authorized'), StreamAuthorizationStatus.authorized);
      expect(StreamAuthorizationStatus.fromString('unavailable'), StreamAuthorizationStatus.unavailable);
      expect(StreamAuthorizationStatus.fromString('pending'), StreamAuthorizationStatus.pending);
    });

    test('fromString returns unknown for null', () {
      expect(StreamAuthorizationStatus.fromString(null), StreamAuthorizationStatus.unknown);
    });
  });

  group('MatchModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 1,
        'provider_name': 'mock',
        'external_id': 2001,
        'league': {
          'id': 1,
          'provider_name': 'mock',
          'external_id': 1001,
          'name': 'Premier League',
        },
        'home_team': {
          'id': 1,
          'provider_name': 'mock',
          'external_id': 101,
          'name': 'Arsenal',
          'short_name': 'ARS',
        },
        'away_team': {
          'id': 2,
          'provider_name': 'mock',
          'external_id': 102,
          'name': 'Chelsea',
          'short_name': 'CHE',
        },
        'status': 'live',
        'minute': 67,
        'home_score': 2,
        'away_score': 1,
        'match_date': '2026-09-15T19:00:00Z',
        'venue': 'Emirates Stadium',
        'events': [],
        'statistics': [],
      };

      final match = MatchModel.fromJson(json);
      expect(match.id, 1);
      expect(match.status, MatchStatus.live);
      expect(match.homeScore, 2);
      expect(match.awayScore, 1);
      expect(match.homeTeam.name, 'Arsenal');
      expect(match.awayTeam.name, 'Chelsea');
      expect(match.league.name, 'Premier League');
      expect(match.venue, 'Emirates Stadium');
    });

    test('fromJson handles missing optional fields', () {
      final json = {
        'id': 1,
        'provider_name': 'mock',
        'external_id': 2001,
        'league': {
          'id': 1,
          'provider_name': 'mock',
          'external_id': 1001,
          'name': 'Test League',
        },
        'home_team': {
          'id': 1,
          'provider_name': 'mock',
          'external_id': 101,
          'name': 'Home',
        },
        'away_team': {
          'id': 2,
          'provider_name': 'mock',
          'external_id': 102,
          'name': 'Away',
        },
        'status': 'scheduled',
        'match_date': '2026-09-15T19:00:00Z',
        'events': [],
        'statistics': [],
      };

      final match = MatchModel.fromJson(json);
      expect(match.minute, isNull);
      expect(match.venue, isNull);
      expect(match.referee, isNull);
    });

    test('scoreLine returns correct format', () {
      final match = MatchModel(
        id: 1,
        providerName: 'mock',
        externalId: 2001,
        league: const LeagueModel(id: 1, providerName: 'mock', externalId: 1001, name: 'Test'),
        homeTeam: const TeamModel(id: 1, providerName: 'mock', externalId: 101, name: 'Home'),
        awayTeam: const TeamModel(id: 2, providerName: 'mock', externalId: 102, name: 'Away'),
        status: MatchStatus.live,
        matchDate: DateTime(2026, 9, 15),
        homeScore: 2,
        awayScore: 1,
      );
      expect(match.scoreLine, '2 - 1');
    });

    test('scoreLine returns 0 - 0 for default scores', () {
      final match = MatchModel(
        id: 1,
        providerName: 'mock',
        externalId: 2001,
        league: const LeagueModel(id: 1, providerName: 'mock', externalId: 1001, name: 'Test'),
        homeTeam: const TeamModel(id: 1, providerName: 'mock', externalId: 101, name: 'Home'),
        awayTeam: const TeamModel(id: 2, providerName: 'mock', externalId: 102, name: 'Away'),
        status: MatchStatus.scheduled,
        matchDate: DateTime(2026, 9, 15),
        homeScore: 0,
        awayScore: 0,
      );
      expect(match.scoreLine, '0 - 0');
    });

    test('statusText returns correct text for live match', () {
      final match = MatchModel(
        id: 1,
        providerName: 'mock',
        externalId: 2001,
        league: const LeagueModel(id: 1, providerName: 'mock', externalId: 1001, name: 'Test'),
        homeTeam: const TeamModel(id: 1, providerName: 'mock', externalId: 101, name: 'Home'),
        awayTeam: const TeamModel(id: 2, providerName: 'mock', externalId: 102, name: 'Away'),
        status: MatchStatus.live,
        matchDate: DateTime(2026, 9, 15),
        minute: 67,
        homeScore: 2,
        awayScore: 1,
      );
      expect(match.statusText, "67'");
    });

    test('statusText returns correct text for finished match', () {
      final match = MatchModel(
        id: 1,
        providerName: 'mock',
        externalId: 2001,
        league: const LeagueModel(id: 1, providerName: 'mock', externalId: 1001, name: 'Test'),
        homeTeam: const TeamModel(id: 1, providerName: 'mock', externalId: 101, name: 'Home'),
        awayTeam: const TeamModel(id: 2, providerName: 'mock', externalId: 102, name: 'Away'),
        status: MatchStatus.finished,
        matchDate: DateTime(2026, 9, 15),
        homeScore: 2,
        awayScore: 1,
      );
      expect(match.statusText, 'Full Time');
    });

    test('statusText returns correct text for scheduled match', () {
      final match = MatchModel(
        id: 1,
        providerName: 'mock',
        externalId: 2001,
        league: const LeagueModel(id: 1, providerName: 'mock', externalId: 1001, name: 'Test'),
        homeTeam: const TeamModel(id: 1, providerName: 'mock', externalId: 101, name: 'Home'),
        awayTeam: const TeamModel(id: 2, providerName: 'mock', externalId: 102, name: 'Away'),
        status: MatchStatus.scheduled,
        matchDate: DateTime(2026, 9, 15, 20, 0),
        homeScore: 0,
        awayScore: 0,
      );
      expect(match.statusText, contains(':'));
    });

    test('statusText returns halftime text', () {
      final match = MatchModel(
        id: 1,
        providerName: 'mock',
        externalId: 2001,
        league: const LeagueModel(id: 1, providerName: 'mock', externalId: 1001, name: 'Test'),
        homeTeam: const TeamModel(id: 1, providerName: 'mock', externalId: 101, name: 'Home'),
        awayTeam: const TeamModel(id: 2, providerName: 'mock', externalId: 102, name: 'Away'),
        status: MatchStatus.halftime,
        matchDate: DateTime(2026, 9, 15),
        homeScore: 1,
        awayScore: 0,
      );
      expect(match.statusText, 'Half Time');
    });
  });

  group('AIAnalysisModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 1,
        'match_id': 1,
        'analysis_type': 'live',
        'interpretation': 'Test analysis',
        'key_insights': ['Insight 1', 'Insight 2'],
        'reference_validation_rate': 1.0,
        'validation_label': 'high',
        'data_references': [
          {'type': 'score', 'key': 'score_line', 'value': '2 - 1'},
        ],
        'validation_result': 'passed',
        'ai_provider': 'mock',
        'generated_at': '2026-09-15T20:00:00Z',
      };

      final analysis = AIAnalysisModel.fromJson(json);
      expect(analysis.interpretation, 'Test analysis');
      expect(analysis.keyInsights.length, 2);
      expect(analysis.referenceValidationRate, 1.0);
      expect(analysis.validationLabel, 'high');
      expect(analysis.dataReferences.length, 1);
      expect(analysis.aiProvider, 'mock');
    });
  });

  group('LeagueModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 1,
        'provider_name': 'mock',
        'external_id': 1001,
        'name': 'Premier League',
        'country': 'England',
        'logo_url': 'https://example.com/logo.png',
        'season': '2026',
      };

      final league = LeagueModel.fromJson(json);
      expect(league.id, 1);
      expect(league.name, 'Premier League');
      expect(league.country, 'England');
      expect(league.logoUrl, 'https://example.com/logo.png');
      expect(league.season, '2026');
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'id': 1,
        'provider_name': 'mock',
        'external_id': 1001,
        'name': 'Test League',
      };

      final league = LeagueModel.fromJson(json);
      expect(league.country, isNull);
      expect(league.logoUrl, isNull);
      expect(league.season, isNull);
    });
  });

  group('TeamModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 1,
        'provider_name': 'mock',
        'external_id': 101,
        'name': 'Arsenal',
        'short_name': 'ARS',
        'logo_url': 'https://example.com/arsenal.png',
      };

      final team = TeamModel.fromJson(json);
      expect(team.id, 1);
      expect(team.name, 'Arsenal');
      expect(team.shortName, 'ARS');
      expect(team.logoUrl, 'https://example.com/arsenal.png');
    });
  });

  group('MatchEventModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 1,
        'event_type': 'goal',
        'minute': 45,
        'player_name': 'Bukayo Saka',
        'assist_player': 'Martin Odegaard',
        'team_id': 1,
        'detail': 'Left-footed shot',
      };

      final event = MatchEventModel.fromJson(json);
      expect(event.eventType, EventType.goal);
      expect(event.minute, 45);
      expect(event.playerName, 'Bukayo Saka');
      expect(event.assistPlayer, 'Martin Odegaard');
    });
  });

  group('MatchStatisticModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 1,
        'stat_type': 'possession',
        'home_value': '58',
        'away_value': '42',
      };

      final stat = MatchStatisticModel.fromJson(json);
      expect(stat.statType, 'possession');
      expect(stat.homeValue, '58');
      expect(stat.awayValue, '42');
    });
  });

  group('StreamInfoModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'available': true,
        'stream': {
          'embed_url': 'https://example.com/stream',
          'provider_name': 'authorized_provider',
          'quality': '1080p',
          'language': 'English',
        },
        'message': 'Stream available',
        'alternatives': 2,
      };

      final stream = StreamInfoModel.fromJson(json);
      expect(stream.available, true);
      expect(stream.embedUrl, 'https://example.com/stream');
      expect(stream.quality, '1080p');
      expect(stream.alternatives, 2);
    });

    test('fromJson handles unavailable stream', () {
      final json = {
        'available': false,
        'message': 'No stream available',
        'alternatives': 0,
      };

      final stream = StreamInfoModel.fromJson(json);
      expect(stream.available, false);
      expect(stream.embedUrl, isNull);
      expect(stream.alternatives, 0);
    });

    test('fromJson handles non-Map stream field gracefully', () {
      final json = {
        'available': false,
        'stream': 'invalid',
        'message': 'No stream',
        'alternatives': 0,
      };

      final stream = StreamInfoModel.fromJson(json);
      expect(stream.available, false);
      expect(stream.embedUrl, isNull);
    });
  });

  group('MatchModel hardening', () {
    test('throws FormatException when id is missing', () {
      final json = {
        'provider_name': 'mock',
        'league': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'L'},
        'home_team': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'H'},
        'away_team': {'id': 2, 'provider_name': 'mock', 'external_id': 2, 'name': 'A'},
        'status': 'live',
        'match_date': '2026-01-01T00:00:00Z',
      };

      expect(() => MatchModel.fromJson(json), throwsFormatException);
    });

    test('throws FormatException when id is null', () {
      final json = {
        'id': null,
        'provider_name': 'mock',
        'league': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'L'},
        'home_team': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'H'},
        'away_team': {'id': 2, 'provider_name': 'mock', 'external_id': 2, 'name': 'A'},
        'status': 'live',
        'match_date': '2026-01-01T00:00:00Z',
      };

      expect(() => MatchModel.fromJson(json), throwsFormatException);
    });

    test('throws FormatException when league is missing', () {
      final json = {
        'id': 1,
        'provider_name': 'mock',
        'home_team': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'H'},
        'away_team': {'id': 2, 'provider_name': 'mock', 'external_id': 2, 'name': 'A'},
        'status': 'live',
        'match_date': '2026-01-01T00:00:00Z',
      };

      expect(() => MatchModel.fromJson(json), throwsFormatException);
    });

    test('throws FormatException when league is wrong type', () {
      final json = {
        'id': 1,
        'provider_name': 'mock',
        'league': 'not_a_map',
        'home_team': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'H'},
        'away_team': {'id': 2, 'provider_name': 'mock', 'external_id': 2, 'name': 'A'},
        'status': 'live',
        'match_date': '2026-01-01T00:00:00Z',
      };

      expect(() => MatchModel.fromJson(json), throwsFormatException);
    });

    test('throws FormatException when home_team is missing', () {
      final json = {
        'id': 1,
        'provider_name': 'mock',
        'league': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'L'},
        'away_team': {'id': 2, 'provider_name': 'mock', 'external_id': 2, 'name': 'A'},
        'status': 'live',
        'match_date': '2026-01-01T00:00:00Z',
      };

      expect(() => MatchModel.fromJson(json), throwsFormatException);
    });

    test('throws FormatException when match_date is missing', () {
      final json = {
        'id': 1,
        'provider_name': 'mock',
        'league': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'L'},
        'home_team': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'H'},
        'away_team': {'id': 2, 'provider_name': 'mock', 'external_id': 2, 'name': 'A'},
        'status': 'live',
      };

      expect(() => MatchModel.fromJson(json), throwsFormatException);
    });

    test('throws FormatException when match_date is malformed', () {
      final json = {
        'id': 1,
        'provider_name': 'mock',
        'league': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'L'},
        'home_team': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'H'},
        'away_team': {'id': 2, 'provider_name': 'mock', 'external_id': 2, 'name': 'A'},
        'status': 'live',
        'match_date': 'not-a-date',
      };

      expect(() => MatchModel.fromJson(json), throwsFormatException);
    });

    test('does not substitute DateTime.now() for missing match_date', () {
      final json = {
        'id': 1,
        'provider_name': 'mock',
        'league': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'L'},
        'home_team': {'id': 1, 'provider_name': 'mock', 'external_id': 1, 'name': 'H'},
        'away_team': {'id': 2, 'provider_name': 'mock', 'external_id': 2, 'name': 'A'},
        'status': 'live',
      };

      expect(() => MatchModel.fromJson(json), throwsFormatException);
    });
  });

  group('MatchEventModel hardening', () {
    test('handles null id gracefully', () {
      final json = {
        'event_type': 'goal',
        'minute': 45,
      };

      final event = MatchEventModel.fromJson(json);
      expect(event.id, 0);
    });

    test('handles non-int id gracefully', () {
      final json = {
        'id': 'not_an_int',
        'event_type': 'goal',
        'minute': 45,
      };

      final event = MatchEventModel.fromJson(json);
      expect(event.id, 0);
    });
  });

  group('MatchStatisticModel hardening', () {
    test('handles null id gracefully', () {
      final json = {
        'stat_type': 'possession',
        'home_value': '58',
        'away_value': '42',
      };

      final stat = MatchStatisticModel.fromJson(json);
      expect(stat.id, 0);
    });

    test('handles non-int id gracefully', () {
      final json = {
        'id': 'not_an_int',
        'stat_type': 'possession',
      };

      final stat = MatchStatisticModel.fromJson(json);
      expect(stat.id, 0);
    });
  });

  group('AIAnalysisModel hardening', () {
    test('throws FormatException when generated_at is missing', () {
      final json = {
        'match_id': 1,
        'analysis_type': 'live',
        'interpretation': 'Test',
      };

      expect(() => AIAnalysisModel.fromJson(json), throwsFormatException);
    });

    test('throws FormatException when generated_at is malformed', () {
      final json = {
        'match_id': 1,
        'analysis_type': 'live',
        'interpretation': 'Test',
        'generated_at': 'not-a-date',
      };

      expect(() => AIAnalysisModel.fromJson(json), throwsFormatException);
    });

    test('does not substitute DateTime.now() for missing generated_at', () {
      final json = {
        'match_id': 1,
        'analysis_type': 'live',
        'interpretation': 'Test',
      };

      expect(() => AIAnalysisModel.fromJson(json), throwsFormatException);
    });
  });
}
