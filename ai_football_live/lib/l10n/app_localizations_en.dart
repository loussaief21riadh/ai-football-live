// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'AI Football Live';

  @override
  String get live => 'Live';

  @override
  String get allMatches => 'All Matches';

  @override
  String get leagues => 'Leagues';

  @override
  String get matchDetail => 'Match Detail';

  @override
  String get events => 'Events';

  @override
  String get statistics => 'Statistics';

  @override
  String get aiAnalysis => 'AI Analysis';

  @override
  String get streamUnavailable => 'No authorized stream available';

  @override
  String get loading => 'Loading...';

  @override
  String get loadingLiveMatches => 'Loading live matches...';

  @override
  String get loadingMatches => 'Loading matches...';

  @override
  String get loadingLeagues => 'Loading leagues...';

  @override
  String get loadingMatch => 'Loading match...';

  @override
  String get noLiveMatches => 'No live matches at the moment';

  @override
  String get noMatches => 'No matches available';

  @override
  String get noLeagues => 'No leagues available';

  @override
  String get matchNotFound => 'Match not found';

  @override
  String get retry => 'Retry';

  @override
  String get verified => 'verified';

  @override
  String get vs => 'vs';

  @override
  String get unknown => 'Unknown';

  @override
  String assistedBy(Object player) {
    return 'Assist: $player';
  }

  @override
  String get highValidation => 'High confidence';

  @override
  String get partialValidation => 'Partial confidence';

  @override
  String get lowValidation => 'Low confidence';

  @override
  String get pullToRefresh => 'Pull to refresh';

  @override
  String get networkError => 'Network error. Please check your connection.';

  @override
  String get serverError => 'Server error. Please try again later.';

  @override
  String get homeTeam => 'Home';

  @override
  String get awayTeam => 'Away';
}
