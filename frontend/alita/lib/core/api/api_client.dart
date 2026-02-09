import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/foundation.dart';

final apiProvider = Provider<Dio>((ref) {
  String baseUrl = 'http://127.0.0.1:8000';
  
  if (!kIsWeb) {
    if (Platform.isAndroid) {
      baseUrl = 'http://10.0.2.2:8000';
    }
  }

  final dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ));
  
  dio.interceptors.add(LogInterceptor(responseBody: true));
  
  return dio;
});
