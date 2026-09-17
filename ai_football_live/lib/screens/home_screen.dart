import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import 'live_matches_tab.dart';
import 'all_matches_tab.dart';
import 'leagues_tab.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.appTitle),
      ),
      body: _buildBody(),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.live_tv),
            label: l10n.live,
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.sports_soccer),
            label: l10n.allMatches,
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.leaderboard),
            label: l10n.leagues,
          ),
        ],
      ),
    );
  }

  Widget _buildBody() {
    switch (_selectedIndex) {
      case 0:
        return const LiveMatchesTab();
      case 1:
        return const AllMatchesTab();
      case 2:
        return const LeaguesTab();
      default:
        return const SizedBox.shrink();
    }
  }
}
