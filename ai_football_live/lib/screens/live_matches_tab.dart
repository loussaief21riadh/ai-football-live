import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_client.dart';
import '../models/models.dart';
import '../widgets/match_card.dart';
import '../widgets/loading_states.dart';
import 'match_detail_screen.dart';

class LiveMatchesTab extends StatefulWidget {
  const LiveMatchesTab({super.key});

  @override
  State<LiveMatchesTab> createState() => _LiveMatchesTabState();
}

class _LiveMatchesTabState extends State<LiveMatchesTab> {
  List<MatchModel> _matches = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadMatches();
  }

  Future<void> _loadMatches() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final apiClient = context.read<ApiClient>();
      final matches = await apiClient.getLiveMatches();
      setState(() {
        _matches = matches;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const LoadingWidget(message: 'Loading live matches...');
    if (_error != null) return AppErrorWidget(message: _error!, onRetry: _loadMatches);
    if (_matches.isEmpty) return const EmptyWidget(message: 'No live matches at the moment');

    return RefreshIndicator(
      onRefresh: _loadMatches,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(vertical: 8),
        itemCount: _matches.length,
        itemBuilder: (context, index) {
          return MatchCard(
            match: _matches[index],
            onTap: () => _navigateToMatch(_matches[index]),
          );
        },
      ),
    );
  }

  void _navigateToMatch(MatchModel match) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => MatchDetailScreen(matchId: match.id),
      ),
    );
  }
}
