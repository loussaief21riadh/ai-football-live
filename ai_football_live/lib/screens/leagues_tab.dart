import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../l10n/app_localizations.dart';
import '../services/api_client.dart';
import '../models/models.dart';
import '../widgets/loading_states.dart';

class LeaguesTab extends StatefulWidget {
  const LeaguesTab({super.key});

  @override
  State<LeaguesTab> createState() => _LeaguesTabState();
}

class _LeaguesTabState extends State<LeaguesTab> {
  List<LeagueModel> _leagues = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadLeagues();
  }

  Future<void> _loadLeagues() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final apiClient = context.read<ApiClient>();
      final leagues = await apiClient.getLeagues();
      setState(() {
        _leagues = leagues;
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

    if (_loading) return LoadingWidget(message: l10n.loadingLeagues);
    if (_error != null) return AppErrorWidget(message: _error!, onRetry: _loadLeagues);
    if (_leagues.isEmpty) return EmptyWidget(message: l10n.noLeagues);

    return RefreshIndicator(
      onRefresh: _loadLeagues,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(vertical: 8),
        itemCount: _leagues.length,
        itemBuilder: (context, index) {
          final league = _leagues[index];
          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: ListTile(
              leading: const Icon(Icons.sports_soccer),
              title: Text(league.name),
              subtitle: Text(league.country ?? ''),
              trailing: Text(league.season ?? ''),
            ),
          );
        },
      ),
    );
  }
}
