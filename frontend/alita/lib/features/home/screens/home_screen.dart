import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_animate/flutter_animate.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Swaraj Women Safety'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () => context.go('/profile'),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // SOS Button - Prominent
            GestureDetector(
              onTap: () {
                // Trigger SOS
              },
              child: Container(
                width: double.infinity,
                height: 120,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFFFF4081), Color(0xFFF50057)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFFFF4081).withOpacity(0.4),
                      blurRadius: 10,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: const Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.sos, size: 48, color: Colors.white),
                    SizedBox(height: 8),
                    Text(
                      'EMERGENCY SOS',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 2,
                      ),
                    ),
                  ],
                ),
              ),
            ).animate().pulse(duration: 2.seconds, curve: Curves.easeInOut),
            const SizedBox(height: 24),
            Expanded(
              child: GridView.count(
                crossAxisCount: 2,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                children: [
                  _buildFeatureCard(context, Icons.location_on, 'Live Location', '/live-location', Colors.purple),
                  _buildFeatureCard(context, Icons.map, 'Safety Map', '/safety-map', Colors.blue),
                  _buildFeatureCard(context, Icons.contact_phone, 'Contacts', '/contacts', Colors.teal),
                  _buildFeatureCard(context, Icons.people, 'Community', '/community', Colors.orange),
                  _buildFeatureCard(context, Icons.report_problem, 'Report', '/report', Colors.redAccent),
                  _buildFeatureCard(context, Icons.chat, 'Chatbot', '/chatbot', Colors.indigo),
                  _buildFeatureCard(context, Icons.library_books, 'Resources', '/resources', Colors.green),
                  _buildFeatureCard(context, Icons.history, 'History', '/history', Colors.grey),
                  _buildFeatureCard(context, Icons.settings, 'Settings', '/settings', Colors.blueGrey),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureCard(BuildContext context, IconData icon, String title, String route, Color color) {
    return GestureDetector(
      onTap: () => context.go(route),
      child: Container(
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 5,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircleAvatar(
              radius: 24,
              backgroundColor: color.withOpacity(0.2),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ],
        ),
      ),
    );
  }
}
