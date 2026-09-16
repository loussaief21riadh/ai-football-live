import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/models.dart';

class ApiException implements Exception {
  final String code;
  final String message;
  final int? statusCode;

  ApiException({required this.code, required this.message, this.statusCode});

  @override
  String toString() => 'ApiException($code): $message';
}

class ApiClient {
  final http.Client _client;
  final String _baseUrl;

  ApiClient({http.Client? client, String? baseUrl})
      : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? ApiConfig.baseUrl;

  Future<Map<String, dynamic>> _get(String path) async {
    final uri = Uri.parse('$_baseUrl$path');
    final response = await _client
        .get(uri)
        .timeout(ApiConfig.timeout);

    if (response.statusCode != 200) {
      String code = 'UNKNOWN_ERROR';
      String message = 'An unexpected error occurred';
      try {
        final body = jsonDecode(response.body);
        final error = body['error'] as Map<String, dynamic>?;
        code = error?['code'] ?? 'UNKNOWN_ERROR';
        message = error?['message'] ?? 'An unexpected error occurred';
      } catch (_) {}
      throw ApiException(
        code: code,
        message: message,
        statusCode: response.statusCode,
      );
    }

    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<List<MatchModel>> getMatches({
    String? status,
    int? leagueId,
    int limit = 20,
    int offset = 0,
  }) async {
    final params = <String, String>{
      'limit': limit.toString(),
      'offset': offset.toString(),
    };
    if (status != null) params['status'] = status;
    if (leagueId != null) params['league_id'] = leagueId.toString();

    final queryString = params.entries
        .map((e) => '${e.key}=${Uri.encodeComponent(e.value)}')
        .join('&');
    final data = await _get('/api/v1/matches?$queryString');
    final list = data['data'] as List<dynamic>;
    return list.map((m) => MatchModel.fromJson(m as Map<String, dynamic>)).toList();
  }

  Future<List<MatchModel>> getLiveMatches() async {
    final data = await _get('/api/v1/matches/live');
    final list = data['data'] as List<dynamic>;
    return list.map((m) => MatchModel.fromJson(m as Map<String, dynamic>)).toList();
  }

  Future<MatchModel> getMatch(int matchId) async {
    final data = await _get('/api/v1/matches/$matchId');
    return MatchModel.fromJson(data['data'] as Map<String, dynamic>);
  }

  Future<List<LeagueModel>> getLeagues() async {
    final data = await _get('/api/v1/leagues');
    final list = data['data'] as List<dynamic>;
    return list.map((l) => LeagueModel.fromJson(l as Map<String, dynamic>)).toList();
  }

  Future<AIAnalysisModel?> getAiAnalysis(int matchId, {String type = 'live'}) async {
    final data = await _get('/api/v1/matches/$matchId/ai-analysis?type=$type');
    final analysisData = data['data'] as Map<String, dynamic>;
    if (analysisData['available'] == false) return null;
    return AIAnalysisModel.fromJson(analysisData);
  }

  Future<StreamInfoModel> getStreamInfo(int matchId) async {
    final data = await _get('/api/v1/matches/$matchId/streams');
    return StreamInfoModel.fromJson(data['data'] as Map<String, dynamic>);
  }

  Future<bool> healthCheck() async {
    try {
      final data = await _get('/api/v1/health');
      return data['status'] == 'ok';
    } catch (_) {
      return false;
    }
  }
}
