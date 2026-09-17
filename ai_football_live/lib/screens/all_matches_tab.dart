import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../l10n/app_localizations.dart';
import '../services/api_client.dart';
import '../models/models.dart';
import '../widgets/match_card.dart';
import '../widgets/loading_states.dart';
import 'match_detail_screen.dart';

class AllMatchesTab extends StatefulWidget {
  const AllMatchesTab({super.key});

  @override
  State<AllMatchesTab> createState() => _AllMatchesTabState();
}

class _AllMatchesTabState extends State<AllMatchesTab> {
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
      final matches = await apiClient.getMatches();
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
    final l10n = AppLocalizations.of(context)!;

    if (_loading) return LoadingWidget(message: l10n.loadingMatches);
    if (_error != null) return AppErrorWidget(message: _error!, onRetry: _loadMatches);
    if (_matches.isEmpty) return EmptyWidget(message: l10n.noMatches);

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
