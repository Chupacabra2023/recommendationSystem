import 'package:flutter/material.dart';
import '../services/app_services.dart';
import '../models/recommendation_models.dart';
import 'package:intl/intl.dart';
import 'package:cloud_firestore/cloud_firestore.dart'; // ← PRIDAJ
import '../utils/category_mapper.dart'; // ← PRIDAJ pre filtrovanie kategórií

class RecommendationsViewScreen extends StatefulWidget {
  final String userId;

  const RecommendationsViewScreen({
    Key? key,
    required this.userId,
  }) : super(key: key);

  @override
  _RecommendationsViewScreenState createState() =>
      _RecommendationsViewScreenState();
}

class _RecommendationsViewScreenState extends State<RecommendationsViewScreen> {
  final _service = AppServices().recommendationService;

  List<ScoredEvent> _recommendations = [];
  Map<String, double> _userProfile = {};
  bool _isLoading = false;
  String? _errorMessage;

  // ← NOVÉ: Sledovanie času
  DateTime? _loadStartTime;
  Duration? _loadDuration;
  String? _userName; // ← NOVÉ: Meno užívateľa

  @override
  void initState() {
    super.initState();
    _loadRecommendations();
  }

  Future<void> _loadRecommendations() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _loadStartTime = DateTime.now(); // ← Začni merať čas
      _loadDuration = null;
    });

    try {
      // Načítaj užívateľa (aby sme mali meno)
      final userDoc = await AppServices().recommendationService;

      // Hack: Načítaj užívateľa priamo z Firestore pre info
      final firestore = FirebaseFirestore.instance;
      final userSnapshot = await firestore
          .collection('users')
          .doc(widget.userId)
          .get();

      if (userSnapshot.exists) {
        _userName = userSnapshot.data()?['name'] ?? 'Unknown';
      }

      // Načítaj profil
      _userProfile = await _service.getUserProfile(widget.userId);

      // Získaj odporúčania
      _recommendations = await _service.getRecommendations(
        userId: widget.userId,
        count: 20,
        maxDistanceKm: 50,
      );

      // ← Vypočítaj čas
      final endTime = DateTime.now();
      _loadDuration = endTime.difference(_loadStartTime!);

      setState(() {
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = 'Chyba: $e';
        _loadDuration = DateTime.now().difference(_loadStartTime!);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '🎯 Odporúčania pre teba',
              style: TextStyle(fontSize: 18),
            ),
            // ← NOVÉ: User ID pod názvom
            Text(
              _userName != null
                  ? '$_userName (${widget.userId})'
                  : widget.userId,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.normal,
                color: Colors.white70,
              ),
            ),
          ],
        ),
        backgroundColor: Colors.deepPurple,
        elevation: 0,
      ),
      body: _buildBody(),
      floatingActionButton: FloatingActionButton(
        onPressed: _loadRecommendations,
        child: Icon(Icons.refresh),
        tooltip: 'Obnoviť',
        backgroundColor: Colors.deepPurple,
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Colors.deepPurple),
            SizedBox(height: 16),
            Text('Hľadám perfektné eventy pre teba...'),
            if (_loadStartTime != null) ...[
              SizedBox(height: 8),
              Text(
                'Čas: ${DateTime.now().difference(_loadStartTime!).inMilliseconds}ms',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
            ],
          ],
        ),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 64, color: Colors.red),
              SizedBox(height: 16),
              Text(
                _errorMessage!,
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.red),
              ),
              SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadRecommendations,
                child: Text('Skúsiť znova'),
              ),
            ],
          ),
        ),
      );
    }

    return Column(
      children: [
        // ← NOVÉ: Info banner s časom načítania
        _buildLoadTimeBanner(),

        // Užívateľský profil
        _buildProfileCard(),

        // Zoznam odporúčaní
        Expanded(
          child: _recommendations.isEmpty
              ? _buildEmptyState()
              : _buildRecommendationsList(),
        ),
      ],
    );
  }

  // ← NOVÁ metóda: Banner s časom načítania
  Widget _buildLoadTimeBanner() {
    if (_loadDuration == null) return SizedBox.shrink();

    return Container(
      width: double.infinity,
      padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.green.shade50, Colors.teal.shade50],
        ),
        border: Border(
          bottom: BorderSide(color: Colors.green.shade200, width: 1),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.speed, size: 20, color: Colors.green.shade700),
          SizedBox(width: 8),
          Text(
            'Načítané za ${_loadDuration!.inMilliseconds}ms',
            style: TextStyle(
              color: Colors.green.shade700,
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
          SizedBox(width: 8),
          Text(
            '(${_recommendations.length} eventov)',
            style: TextStyle(
              color: Colors.green.shade600,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProfileCard() {
    return Container(
      margin: EdgeInsets.all(16),
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.deepPurple.shade50, Colors.blue.shade50],
        ),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.person, color: Colors.deepPurple),
              SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Tvoj profil preferencií',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.deepPurple,
                      ),
                    ),
                    // ← NOVÉ: Zobraz ID a meno
                    Text(
                      _userName ?? widget.userId,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.deepPurple.shade300,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          SizedBox(height: 12),

          if (_userProfile.isEmpty)
            Text(
              'Ešte si nenavštívil žiadne eventy. Skús sa prihlásiť na nejaký event!',
              style: TextStyle(color: Colors.grey[600]),
            )
          else
            ...(
                _userProfile.entries
                    .where((entry) => CategoryMapper.isMainCategory(entry.key)) // ← Len hlavné kategórie
                    .toList()
                  ..sort((a, b) => b.value.compareTo(a.value))
            )
                .map((entry) => Padding(
              padding: EdgeInsets.symmetric(vertical: 6),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          entry.key,
                          style: TextStyle(fontWeight: FontWeight.w500),
                        ),
                      ),
                      Text(
                        '${(entry.value * 100).toInt()}%',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.deepPurple,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 4),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: entry.value,
                      minHeight: 8,
                      backgroundColor: Colors.grey[300],
                      valueColor:
                      AlwaysStoppedAnimation(Colors.deepPurple),
                    ),
                  ),
                ],
              ),
            ))
                .toList(),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.search_off,
              size: 80,
              color: Colors.grey[400],
            ),
            SizedBox(height: 16),
            Text(
              'Žiadne odporúčania',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Momentálne nemáme žiadne vhodné eventy pre teba. Skús navštíviť viac eventov!',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendationsList() {
    return ListView.builder(
      padding: EdgeInsets.symmetric(horizontal: 16),
      itemCount: _recommendations.length,
      itemBuilder: (context, index) {
        return _buildRecommendationCard(
          _recommendations[index],
          index + 1,
        );
      },
    );
  }

  Widget _buildRecommendationCard(ScoredEvent scored, int rank) {
    final event = scored.event;
    final breakdown = scored.scoreBreakdown;

    Color rankColor = rank <= 3
        ? Colors.amber
        : rank <= 10
        ? Colors.green
        : Colors.blue;

    return Card(
      margin: EdgeInsets.only(bottom: 12),
      elevation: 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: ExpansionTile(
        leading: CircleAvatar(
          backgroundColor: rankColor,
          child: Text(
            '#$rank',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          event.title,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        subtitle: Padding(
          padding: EdgeInsets.only(top: 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildInfoRow(
                Icons.category,
                event.category,
                Colors.purple,
              ),
              SizedBox(height: 4),
              _buildInfoRow(
                Icons.location_on,
                '${breakdown['distance_km']?.toStringAsFixed(1)} km',
                Colors.blue,
              ),
              SizedBox(height: 4),
              _buildInfoRow(
                Icons.calendar_today,
                DateFormat('d. MMM yyyy, HH:mm').format(event.date),
                Colors.orange,
              ),
              SizedBox(height: 4),
              _buildInfoRow(
                Icons.star,
                '${event.rating.toStringAsFixed(1)} (${event.totalRatings})',
                Colors.amber,
              ),
              SizedBox(height: 8),

              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: scored.score,
                  minHeight: 20,
                  backgroundColor: Colors.grey[300],
                  valueColor: AlwaysStoppedAnimation(Colors.green),
                ),
              ),
              SizedBox(height: 4),
              Text(
                'Match: ${(scored.score * 100).toInt()}%',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
            ],
          ),
        ),
        children: [
          _buildScoreBreakdown(breakdown),
        ],
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String text, Color color) {
    return Row(
      children: [
        Icon(icon, size: 16, color: color),
        SizedBox(width: 4),
        Expanded(
          child: Text(
            text,
            style: TextStyle(fontSize: 14),
          ),
        ),
      ],
    );
  }

  Widget _buildScoreBreakdown(Map<String, double> breakdown) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(12),
          bottomRight: Radius.circular(12),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '📊 Podrobný breakdown skóre',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
          SizedBox(height: 12),

          _buildScoreRow(
            'Kategória',
            breakdown['main_category']!,
            breakdown['main_category_match']!,
            Icons.category,
            Colors.purple,
          ),
          _buildScoreRow(

            'Podkategória',  // 🔥 NOVÉ
            breakdown['sub_category'] ?? 0,
            breakdown['sub_category_match'] ?? 0,
            Icons.category_outlined,
            Colors.deepPurple,
          ),
          _buildScoreRow(
            'Vzdialenosť',
            breakdown['distance']!,
            breakdown['distance']! / 0.3,
            Icons.location_on,
            Colors.blue,
          ),
          _buildScoreRow(
            'Rating',
            breakdown['rating']!,
            breakdown['rating_value']! / 5.0,
            Icons.star,
            Colors.amber,
          ),
          _buildScoreRow(
            'Popularita',
            breakdown['popularity']!,
            breakdown['attendees_count']! / 100,
            Icons.people,
            Colors.green,
          ),
        ],
      ),
    );
  }

  Widget _buildScoreRow(
      String label,
      double score,
      double normalizedValue,
      IconData icon,
      Color color,
      ) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 6),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: color),
              SizedBox(width: 8),
              Expanded(child: Text(label)),
              Text(
                '${(score * 100).toInt()}%',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
          SizedBox(height: 4),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: normalizedValue.clamp(0.0, 1.0),
              minHeight: 6,
              backgroundColor: Colors.grey[300],
              valueColor: AlwaysStoppedAnimation(color),
            ),
          ),
        ],
      ),
    );
  }
}
