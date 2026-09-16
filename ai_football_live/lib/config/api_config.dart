class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );
  static const Duration timeout = Duration(seconds: 10);
  static const Duration aiTimeout = Duration(seconds: 30);
}
