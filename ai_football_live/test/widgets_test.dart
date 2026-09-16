import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ai_football_live/widgets/loading_states.dart';
import 'package:ai_football_live/models/enums.dart';
import 'package:ai_football_live/models/models.dart';
import 'package:ai_football_live/widgets/match_card.dart';

void main() {
  group('LoadingWidget', () {
    testWidgets('shows message when provided', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: LoadingWidget(message: 'Loading data...'),
          ),
        ),
      );
      expect(find.text('Loading data...'), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows no message when null', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: LoadingWidget(),
          ),
        ),
      );
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('Loading data...'), findsNothing);
    });
  });

  group('AppErrorWidget', () {
    testWidgets('shows error message', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppErrorWidget(message: 'Something went wrong'),
          ),
        ),
      );
      expect(find.text('Something went wrong'), findsOneWidget);
      expect(find.byIcon(Icons.error_outline), findsOneWidget);
    });

    testWidgets('shows retry button when onRetry provided', (WidgetTester tester) async {
      bool retryPressed = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppErrorWidget(
              message: 'Error',
              onRetry: () => retryPressed = true,
            ),
          ),
        ),
      );
      expect(find.text('Retry'), findsOneWidget);
      await tester.tap(find.text('Retry'));
      expect(retryPressed, true);
    });

    testWidgets('hides retry button when onRetry is null', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppErrorWidget(message: 'Error'),
          ),
        ),
      );
      expect(find.text('Retry'), findsNothing);
    });
  });

  group('EmptyWidget', () {
    testWidgets('shows message and icon', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: EmptyWidget(message: 'No data available'),
          ),
        ),
      );
      expect(find.text('No data available'), findsOneWidget);
      expect(find.byIcon(Icons.sports_soccer), findsOneWidget);
    });
  });

  group('NoStreamPlaceholder', () {
    testWidgets('shows default message', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: NoStreamPlaceholder(),
          ),
        ),
      );
      expect(find.text('No authorized stream available for this match'), findsOneWidget);
      expect(find.byIcon(Icons.videocam_off), findsOneWidget);
    });

    testWidgets('shows custom message', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: NoStreamPlaceholder(message: 'Custom message'),
          ),
        ),
      );
      expect(find.text('Custom message'), findsOneWidget);
    });
  });

  group('MatchCard', () {
    final testMatch = MatchModel(
      id: 1,
      providerName: 'mock',
      externalId: 2001,
      league: const LeagueModel(id: 1, providerName: 'mock', externalId: 1001, name: 'Premier League'),
      homeTeam: const TeamModel(id: 1, providerName: 'mock', externalId: 101, name: 'Arsenal', shortName: 'ARS'),
      awayTeam: const TeamModel(id: 2, providerName: 'mock', externalId: 102, name: 'Chelsea', shortName: 'CHE'),
      status: MatchStatus.live,
      matchDate: DateTime(2026, 9, 15),
      minute: 67,
      homeScore: 2,
      awayScore: 1,
    );

    testWidgets('displays team names', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MatchCard(match: testMatch),
          ),
        ),
      );
      expect(find.text('Arsenal'), findsOneWidget);
      expect(find.text('Chelsea'), findsOneWidget);
    });

    testWidgets('displays score', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MatchCard(match: testMatch),
          ),
        ),
      );
      expect(find.text('2'), findsOneWidget);
      expect(find.text('-'), findsOneWidget);
      expect(find.text('1'), findsOneWidget);
    });

    testWidgets('displays league name', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MatchCard(match: testMatch),
          ),
        ),
      );
      expect(find.text('Premier League'), findsOneWidget);
    });

    testWidgets('calls onTap when tapped', (WidgetTester tester) async {
      bool tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MatchCard(
              match: testMatch,
              onTap: () => tapped = true,
            ),
          ),
        ),
      );
      await tester.tap(find.byType(MatchCard));
      expect(tapped, true);
    });
  });

  group('LiveScoreBadge', () {
    testWidgets('shows live status in red', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: LiveScoreBadge(status: MatchStatus.live, statusText: "67'"),
          ),
        ),
      );
      expect(find.text("67'"), findsOneWidget);
    });

    testWidgets('shows finished status', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: LiveScoreBadge(status: MatchStatus.finished, statusText: 'Full Time'),
          ),
        ),
      );
      expect(find.text('Full Time'), findsOneWidget);
    });

    testWidgets('shows scheduled status', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: LiveScoreBadge(status: MatchStatus.scheduled, statusText: '20:00'),
          ),
        ),
      );
      expect(find.text('20:00'), findsOneWidget);
    });
  });
}
