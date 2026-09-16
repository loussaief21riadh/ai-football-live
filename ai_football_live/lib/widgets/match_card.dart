import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../models/enums.dart';
import '../models/models.dart';

class MatchCard extends StatelessWidget {
  final MatchModel match;
  final VoidCallback? onTap;

  const MatchCard({super.key, required this.match, this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(),
              const SizedBox(height: 12),
              _buildScore(),
              const SizedBox(height: 8),
              _buildTeams(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          match.league.name,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.grey,
            fontWeight: FontWeight.w500,
          ),
        ),
        LiveScoreBadge(status: match.status, statusText: match.statusText),
      ],
    );
  }

  Widget _buildScore() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          match.homeScore.toString(),
          style: const TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.bold,
          ),
        ),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            '-',
            style: TextStyle(
              fontSize: 24,
              color: Colors.grey,
            ),
          ),
        ),
        Text(
          match.awayScore.toString(),
          style: const TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildTeams() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Text(
            match.homeTeam.name,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
          ),
        ),
        Expanded(
          child: Text(
            match.awayTeam.name,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
          ),
        ),
      ],
    );
  }
}

class LiveScoreBadge extends StatelessWidget {
  final MatchStatus status;
  final String statusText;

  const LiveScoreBadge({
    super.key,
    required this.status,
    required this.statusText,
  });

  @override
  Widget build(BuildContext context) {
    Color backgroundColor;
    Color textColor = Colors.white;

    switch (status) {
      case MatchStatus.live:
      case MatchStatus.halftime:
        backgroundColor = AppTheme.liveColor;
        break;
      case MatchStatus.finished:
        backgroundColor = AppTheme.finishedColor;
        break;
      case MatchStatus.scheduled:
        backgroundColor = AppTheme.scheduledColor;
        break;
      default:
        backgroundColor = Colors.grey;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        statusText,
        style: TextStyle(
          color: textColor,
          fontSize: 11,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}
