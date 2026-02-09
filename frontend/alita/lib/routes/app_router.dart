import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:alita/features/splash/splash_screen.dart';
import 'package:alita/features/onboarding/onboarding_screen.dart';
import 'package:alita/features/auth/screens/login_screen.dart';
import 'package:alita/features/auth/screens/register_screen.dart';
import 'package:alita/features/home/screens/home_screen.dart';

final GoRouter appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: '/onboarding',
      builder: (context, state) => const OnboardingScreen(),
    ),
    GoRoute(
      path: '/auth/login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/auth/register',
      builder: (context, state) => const RegisterScreen(),
    ),
    GoRoute(
      path: '/home',
      builder: (context, state) => const HomeScreen(),
    ),
    // Placeholder routes for features
    GoRoute(
      path: '/sos',
      builder: (context, state) => const Scaffold(body: Center(child: Text('SOS Screen'))),
    ),
    GoRoute(
      path: '/live-location',
      builder: (context, state) => const Scaffold(body: Center(child: Text('Live Location'))),
    ),
    GoRoute(
      path: '/safety-map',
      builder: (context, state) => const Scaffold(body: Center(child: Text('Safety Map'))),
    ),
    GoRoute(
      path: '/contacts',
      builder: (context, state) => const Scaffold(body: Center(child: Text('Contacts'))),
    ),
    GoRoute(
      path: '/community',
      builder: (context, state) => const Scaffold(body: Center(child: Text('Community'))),
    ),
    GoRoute(
      path: '/report',
      builder: (context, state) => const Scaffold(body: Center(child: Text('Report'))),
    ),
    GoRoute(
      path: '/chatbot',
      builder: (context, state) => const Scaffold(body: Center(child: Text('Chatbot'))),
    ),
    GoRoute(
      path: '/resources',
      builder: (context, state) => const Scaffold(body: Center(child: Text('Resources'))),
    ),
    GoRoute(
      path: '/profile',
      builder: (context, state) => const Scaffold(body: Center(child: Text('Profile'))),
    ),
    GoRoute(
      path: '/settings',
      builder: (context, state) => const Scaffold(body: Center(child: Text('Settings'))),
    ),
    GoRoute(
      path: '/history',
      builder: (context, state) => const Scaffold(body: Center(child: Text('History'))),
    ),
  ],
);
