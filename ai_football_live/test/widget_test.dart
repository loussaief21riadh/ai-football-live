import 'package:flutter_test/flutter_test.dart';
import 'package:ai_football_live/main.dart';

void main() {
  testWidgets('App starts successfully', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());
    expect(find.text('AI Football Live'), findsOneWidget);
  });
}
