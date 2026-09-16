import 'package:flutter/material.dart';
import '../services/api_client.dart';
import '../models/enums.dart';
import '../models/models.dart';
import '../widgets/match_card.dart';
import '../widgets/loading_states.dart' as widgets;

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Football Live'),
      ),
      body: _buildBody(),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.live_tv),
            label: 'Live',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.sports_soccer),
            label: 'All Matches',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.leaderboard),
            label: 'Leagues',
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

class LiveMatchesTab extends StatefulWidget {
  const LiveMatchesTab({super.key});

  @override
  State<LiveMatchesTab> createState() => _LiveMatchesTabState();
}

class _LiveMatchesTabState extends State<LiveMatchesTab> {
  final ApiClient _apiClient = ApiClient();
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
      final matches = await _apiClient.getLiveMatches();
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
    if (_loading) return const widgets.LoadingWidget(message: 'Loading live matches...');
    if (_error != null) return widgets.ErrorWidget(message: _error!, onRetry: _loadMatches);
    if (_matches.isEmpty) return const widgets.EmptyWidget(message: 'No live matches at the moment');

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

class AllMatchesTab extends StatefulWidget {
  const AllMatchesTab({super.key});

  @override
  State<AllMatchesTab> createState() => _AllMatchesTabState();
}

class _AllMatchesTabState extends State<AllMatchesTab> {
  final ApiClient _apiClient = ApiClient();
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
      final matches = await _apiClient.getMatches();
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
    if (_loading) return const widgets.LoadingWidget(message: 'Loading matches...');
    if (_error != null) return widgets.ErrorWidget(message: _error!, onRetry: _loadMatches);
    if (_matches.isEmpty) return const widgets.EmptyWidget(message: 'No matches available');

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

class LeaguesTab extends StatefulWidget {
  const LeaguesTab({super.key});

  @override
  State<LeaguesTab> createState() => _LeaguesTabState();
}

class _LeaguesTabState extends State<LeaguesTab> {
  final ApiClient _apiClient = ApiClient();
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
      final leagues = await _apiClient.getLeagues();
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
    if (_loading) return const widgets.LoadingWidget(message: 'Loading leagues...');
    if (_error != null) return widgets.ErrorWidget(message: _error!, onRetry: _loadLeagues);
    if (_leagues.isEmpty) return const widgets.EmptyWidget(message: 'No leagues available');

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

class MatchDetailScreen extends StatefulWidget {
  final int matchId;

  const MatchDetailScreen({super.key, required this.matchId});

  @override
  State<MatchDetailScreen> createState() => _MatchDetailScreenState();
}

class _MatchDetailScreenState extends State<MatchDetailScreen> {
  final ApiClient _apiClient = ApiClient();
  MatchModel? _match;
  AIAnalysisModel? _analysis;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadMatch();
  }

  Future<void> _loadMatch() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final match = await _apiClient.getMatch(widget.matchId);
      final analysis = await _apiClient.getAiAnalysis(widget.matchId);
      setState(() {
        _match = match;
        _analysis = analysis;
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
    return Scaffold(
      appBar: AppBar(
        title: Text(_match != null
            ? '${_match!.homeTeam.shortName ?? _match!.homeTeam.name} vs ${_match!.awayTeam.shortName ?? _match!.awayTeam.name}'
            : 'Match Detail'),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) return const widgets.LoadingWidget(message: 'Loading match...');
    if (_error != null) return widgets.ErrorWidget(message: _error!, onRetry: _loadMatch);
    if (_match == null) return const widgets.EmptyWidget(message: 'Match not found');

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildMatchHeader(),
          const SizedBox(height: 16),
          _buildStreamSection(),
          const SizedBox(height: 16),
          if (_match!.events.isNotEmpty) ...[
            _buildEventsSection(),
            const SizedBox(height: 16),
          ],
          if (_match!.statistics.isNotEmpty) ...[
            _buildStatisticsSection(),
            const SizedBox(height: 16),
          ],
          if (_analysis != null) ...[
            _buildAnalysisSection(),
          ],
        ],
      ),
    );
  }

  Widget _buildMatchHeader() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(
              _match!.league.name,
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
            const SizedBox(height: 8),
            LiveScoreBadge(status: _match!.status, statusText: _match!.statusText),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Expanded(
                  child: Column(
                    children: [
                      Text(
                        _match!.homeTeam.name,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
                Text(
                  _match!.scoreLine,
                  style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                ),
                Expanded(
                  child: Column(
                    children: [
                      Text(
                        _match!.awayTeam.name,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            if (_match!.venue != null) ...[
              const SizedBox(height: 8),
              Text(
                _match!.venue!,
                style: const TextStyle(color: Colors.grey, fontSize: 12),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStreamSection() {
    return const widgets.NoStreamPlaceholder();
  }

  Widget _buildEventsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Events',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            ...(_match!.events.map((event) => _buildEventItem(event))),
          ],
        ),
      ),
    );
  }

  Widget _buildEventItem(MatchEventModel event) {
    IconData icon;
    Color color;

    switch (event.eventType) {
      case EventType.goal:
      case EventType.penaltyScored:
        icon = Icons.sports_soccer;
        color = Colors.green;
        break;
      case EventType.ownGoal:
        icon = Icons.sports_soccer;
        color = Colors.orange;
        break;
      case EventType.yellowCard:
        icon = Icons.square;
        color = Colors.yellow;
        break;
      case EventType.redCard:
        icon = Icons.square;
        color = Colors.red;
        break;
      case EventType.substitution:
        icon = Icons.swap_horiz;
        color = Colors.blue;
        break;
      default:
        icon = Icons.circle;
        color = Colors.grey;
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 40,
            child: Text(
              "${event.minute}'",
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(event.playerName ?? 'Unknown'),
          ),
          if (event.assistPlayer != null)
            Text(
              '(Assist: ${event.assistPlayer})',
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
        ],
      ),
    );
  }

  Widget _buildStatisticsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Statistics',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            ...(_match!.statistics.map((stat) => _buildStatItem(stat))),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(MatchStatisticModel stat) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Expanded(
            child: Text(
              stat.homeValue ?? '-',
              textAlign: TextAlign.right,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(
            flex: 2,
            child: Text(
              stat.statType.replaceAll('_', ' ').toUpperCase(),
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ),
          Expanded(
            child: Text(
              stat.awayValue ?? '-',
              textAlign: TextAlign.left,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalysisSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'AI Analysis',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _analysis!.validationLabel == 'high'
                        ? Colors.green[100]
                        : _analysis!.validationLabel == 'partial'
                            ? Colors.orange[100]
                            : Colors.red[100],
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    '${(_analysis!.referenceValidationRate * 100).round()}% verified',
                    style: const TextStyle(fontSize: 11),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(_analysis!.interpretation),
            const SizedBox(height: 8),
            ...(_analysis!.keyInsights.map((insight) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 2),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('• ', style: TextStyle(fontWeight: FontWeight.bold)),
                  Expanded(child: Text(insight)),
                ],
              ),
            ))),
          ],
        ),
      ),
    );
  }
}
