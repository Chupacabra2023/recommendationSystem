import 'package:flutter/material.dart';
import '../services/test_data_generator.dart';
import 'dart:math'; // ← PRIDAJ
import 'recommendations_view_screen.dart'; // ← PRIDAJ

class RecommendationTestScreen extends StatefulWidget {
  @override
  _RecommendationTestScreenState createState() => _RecommendationTestScreenState();
}

class _RecommendationTestScreenState extends State<RecommendationTestScreen> {
  final TestDataGenerator _generator = TestDataGenerator();
  bool _isLoading = false;
  String _statusMessage = 'Pripravený na testovanie';

  Future<void> _runAction(String action, Future<void> Function() task) async {
    setState(() {
      _isLoading = true;
      _statusMessage = action;
    });

    try {
      await task();
      setState(() {
        _statusMessage = '✅ $action - Hotovo!';
      });
    } catch (e) {
      setState(() {
        _statusMessage = '❌ Chyba: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('🧪 Testovanie odporúčaní'),
        backgroundColor: Colors.deepPurple,
      ),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Status panel
            Container(
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                children: [
                  if (_isLoading) CircularProgressIndicator(),
                  SizedBox(height: 8),
                  Text(
                    _statusMessage,
                    style: TextStyle(fontSize: 16),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),

            SizedBox(height: 24),

            Text(
              'Krok 1: Príprava dát',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 12),

            ElevatedButton.icon(
              onPressed: _isLoading ? null : () {
                _runAction(
                  'Generujem 100 užívateľov...',
                      () => _generator.generateTestUsers(200),
                );
              },
              icon: Icon(Icons.people),
              label: Text('Vytvor 100 užívateľov'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.all(16),
                backgroundColor: Colors.blue,
              ),
            ),

            SizedBox(height: 8),

            ElevatedButton.icon(
              onPressed: _isLoading ? null : () {
                _runAction(
                  'Generujem 50 udalostí...',
                      () => _generator.generateTestEvents(200),
                );
              },
              icon: Icon(Icons.event),
              label: Text('Vytvor 50 udalostí'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.all(16),
                backgroundColor: Colors.green,
              ),
            ),
            SizedBox(height: 24),
            Divider(),

            Text(
              'Krok 2: Testovanie odporúčaní',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 12),

            ElevatedButton.icon(
              onPressed: _isLoading ? null : () async {
                // Vyber náhodného užívateľa
                final randomUserId = 'test_user_${Random().nextInt(100)}';

                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => RecommendationsViewScreen(
                      userId: randomUserId,
                    ),
                  ),
                );
              },
              icon: Icon(Icons.lightbulb),
              label: Text('Ukáž odporúčania pre náhodného užívateľa'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.all(16),
                backgroundColor: Colors.orange,
              ),
            ),

            SizedBox(height: 8),

            ElevatedButton.icon(
              onPressed: _isLoading ? null : () {
                _runAction(
                  'Mažem testovacie dáta...',
                      () => _generator.clearTestData(),
                );
              },
              icon: Icon(Icons.delete),
              label: Text('Vymaž testovacie dáta'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.all(16),
                backgroundColor: Colors.red,
              ),
            ),

          ],
        ),
      ),
    );
  }
}