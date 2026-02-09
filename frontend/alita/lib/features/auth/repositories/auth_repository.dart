import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:alita/core/api/api_client.dart';
import 'package:shared_preferences/shared_preferences.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final dio = ref.read(apiProvider);
  return AuthRepository(dio);
});

class AuthRepository {
  final Dio _dio;

  AuthRepository(this._dio);

  Future<void> login(String email, String password) async {
    try {
      final response = await _dio.post(
        '/auth/token',
        data: {'username': email, 'password': password},
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );
      
      if (response.statusCode == 200) {
        final token = response.data['access_token'];
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('token', token);
      } else {
        throw Exception('Login failed: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception(e.response?.data['detail'] ?? 'Login failed');
    } catch (e) {
      throw Exception('An unexpected error occurred: ${e.toString()}');
    }
  }

  Future<void> register(String name, String email, String password) async {
    try {
      final response = await _dio.post(
        '/auth/',
        data: {'name': name, 'email': email, 'password': password},
      );
       if (response.statusCode != 201 && response.statusCode != 200) {
        throw Exception('Registration failed: ${response.statusCode}');
      }
    } on DioException catch (e) {
       throw Exception(e.response?.data['detail'] ?? 'Registration failed');
    } catch (e) {
      throw Exception('An unexpected error occurred: ${e.toString()}');
    }
  }
}
