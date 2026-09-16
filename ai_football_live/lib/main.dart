import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/theme.dart';
import 'services/api_client.dart';
import 'screens/home_screen.dart';
import 'screens/match_detail_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return Provider<ApiClient>(
      create: (_) => ApiClient(),
      child: MaterialApp(
        title: 'AI Football Live',
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.system,
        home: const HomeScreen(),
        onGenerateRoute: (settings) {
          if (settings.name == '/match') {
            final matchId = settings.arguments as int;
            return MaterialPageRoute(
              builder: (context) => MatchDetailScreen(matchId: matchId),
            );
          }
          return null;
        },
      ),
    );
  }
}
