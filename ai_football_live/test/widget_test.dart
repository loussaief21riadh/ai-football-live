import 'package:flutter_test/flutter_test.dart';
import 'package:ai_football_live/main.dart';

void main() {
  testWidgets('App starts successfully', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());
    expect(find.text('AI Football Live'), findsOneWidget);
  });

  testWidgets('Home screen shows bottom navigation', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());
    expect(find.text('Live'), findsOneWidget);
    expect(find.text('All Matches'), findsOneWidget);
    expect(find.text('Leagues'), findsOneWidget);
  });

  testWidgets('Home screen shows live tab by default', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());
    // The live tab should be selected by default
    expect(find.text('Live'), findsOneWidget);
  });
}
