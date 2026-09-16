import 'package:flutter_test/flutter_test.dart';
import 'package:ai_football_live/models/enums.dart';
import 'package:ai_football_live/models/models.dart';

void main() {
  group('MatchStatus', () {
    test('fromString returns correct status', () {
      expect(MatchStatus.fromString('live'), MatchStatus.live);
      expect(MatchStatus.fromString('scheduled'), MatchStatus.scheduled);
      expect(MatchStatus.fromString('finished'), MatchStatus.finished);
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
    });
  });

  group('EventType', () {
    test('fromString returns correct type', () {
      expect(EventType.fromString('goal'), EventType.goal);
      expect(EventType.fromString('yellow_card'), EventType.yellowCard);
      expect(EventType.fromString('red_card'), EventType.redCard);
    });

    test('fromString returns unknown for null', () {
      expect(EventType.fromString(null), EventType.unknown);
    });

    test('fromString returns unknown for invalid value', () {
      expect(EventType.fromString('invalid'), EventType.unknown);
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
  });

  group('AIAnalysisModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 1,
        'match_id': 1,
        'analysis_type': 'live',
        'interpretation': 'Test analysis',
        'key_insights': ['Insight 1'],
        'reference_validation_rate': 1.0,
        'validation_label': 'high',
        'data_references': [],
        'validation_result': 'passed',
        'ai_provider': 'mock',
        'generated_at': '2026-09-15T20:00:00Z',
      };

      final analysis = AIAnalysisModel.fromJson(json);
      expect(analysis.interpretation, 'Test analysis');
      expect(analysis.referenceValidationRate, 1.0);
      expect(analysis.validationLabel, 'high');
    });
  });
}
