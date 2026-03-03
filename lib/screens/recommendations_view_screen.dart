import 'package:flutter/material.dart';
import '../services/app_services.dart';
import '../models/recommendation_models.dart';
import 'package:intl/intl.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../utils/category_mapper.dart';
import '../services/recommendation_engine.dart'; // 🔥 NOVÉ: Import váh
import 'dart:io'; // 🔥 Pre prácu so súbormi
import 'package:path_provider/path_provider.dart'; // 🔥 Pre získanie cesty
import 'package:share_plus/share_plus.dart'; // 🔥 Pre zdieľanie súboru
import 'package:flutter/foundation.dart' show kIsWeb; // 🔥 Pre detekciu web platformy
import '../utils/web_download.dart' as web_download; // 🔥 Web download utility



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

  // 🔥 NOVÁ metóda: Export výsledkov do textového súboru
  Future<void> _exportResults() async {
    try {
      if (_recommendations.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text("Žiadne výsledky na export"))
        );
        return;
      }

      // 🔥 Načítaj používateľa
      final firestore = FirebaseFirestore.instance;
      final userDoc = await firestore.collection('users').doc(widget.userId).get();

      List<String> visitedIds = [];
      List<String> favoriteIds = [];

      List<String> visitedTitles = [];
      List<String> favoriteTitles = [];

      if (userDoc.exists) {
        visitedIds = List<String>.from(userDoc['visitedEventIds'] ?? []);
        favoriteIds = List<String>.from(userDoc['favoriteEventIds'] ?? []);
      }

// 🔥 Načítaj názvy eventov
      Future<List<String>> loadTitles(List<String> ids) async {
        List<String> titles = [];
        for (String id in ids) {
          final doc = await firestore.collection('events').doc(id).get();
          if (doc.exists) {
            final data = doc.data()!;
            final title = data['title'] ?? 'Unknown';
            final category = data['category'] ?? 'Unknown';
            final mainCat = CategoryMapper.getMainCategory(category);

            titles.add("$title ($mainCat / $category)");
          }
        }
        return titles;
      }

      visitedTitles = await loadTitles(visitedIds);
      favoriteTitles = await loadTitles(favoriteIds);

      final topEvents = _recommendations.take(5).toList();

      // 🔥 Vytvor textový export
      StringBuffer buffer = StringBuffer();

      buffer.writeln("========= EXPORT ODPORÚČANÍ =========\n");
      buffer.writeln("📅 Dátum: ${DateTime.now()}");
      buffer.writeln("👤 Užívateľ: ${_userName ?? widget.userId}");
      buffer.writeln("TOP 5 eventov:\n");

      for (int i = 0; i < topEvents.length; i++) {
        final scored = topEvents[i];
        final e = scored.event;
        final b = scored.scoreBreakdown;

        buffer.writeln("--------------------------------------------------");
        buffer.writeln("#${i + 1}  ${e.title}");
        buffer.writeln("Celkové skóre: ${(scored.score * 100).toStringAsFixed(1)}%");
        buffer.writeln("Kategória: ${CategoryMapper.getMainCategory(e.category)} / ${e.category}");
        buffer.writeln("Vzdialenosť: ${b['distance_km']?.toStringAsFixed(2)} km");
        buffer.writeln("Rating: ${e.rating.toStringAsFixed(1)} z 5 (${e.totalRatings} hodnotení)");
        buffer.writeln("Účastníci: ${e.attendees.length}/${e.maxAttendees}" +
          (e.attendees.length >= e.maxAttendees ? " - PLNÉ ❌" : ""));

        buffer.writeln("\n--- BREAKDOWN ---");
        buffer.writeln("Hlavná kategória: ${(b['main_category']! * 100).toStringAsFixed(1)}%  (zhoda ${(b['main_category_match']! * 100).toStringAsFixed(1)}%)");
        buffer.writeln("Podkategória: ${(b['sub_category']! * 100).toStringAsFixed(1)}%  (zhoda ${(b['sub_category_match']! * 100).toStringAsFixed(1)}%)");
        buffer.writeln("Vzdialenosť: ${(b['distance']! * 100).toStringAsFixed(1)}%");
        buffer.writeln("Rating: ${(b['rating']! * 100).toStringAsFixed(1)}%");
        buffer.writeln("Popularita: ${(b['popularity']! * 100).toStringAsFixed(1)}%");

        if (b['favorite_bonus'] != null && b['favorite_bonus']! > 0) {
          buffer.writeln("Obľúbený bonus: ${(b['favorite_bonus']! * 100).toStringAsFixed(1)}%");
        }

        buffer.writeln("");
      }

      // 🔥 Pridaj váhy
      buffer.writeln("========= NASTAVENIE VÁH =========\n");
      buffer.writeln("Hlavná kategória: ${(RecommendationEngine.MAIN_CATEGORY_WEIGHT * 100).toStringAsFixed(2)}%");
      buffer.writeln("Podkategória: ${(RecommendationEngine.SUB_CATEGORY_WEIGHT * 100).toStringAsFixed(2)}%");
      buffer.writeln("Vzdialenosť: ${(RecommendationEngine.DISTANCE_WEIGHT * 100).toStringAsFixed(2)}%");
      buffer.writeln("Rating: ${(RecommendationEngine.RATING_WEIGHT * 100).toStringAsFixed(2)}%");
      buffer.writeln("Popularita: ${(RecommendationEngine.POPULARITY_WEIGHT * 100).toStringAsFixed(2)}%");
      buffer.writeln("Obľúbený bonus: ${(RecommendationEngine.FAVORITE_SUBCATEGORY_BONUS * 100).toStringAsFixed(2)}%");


      buffer.writeln("========= PROFIL UŽÍVATEĽA =========\n");
      buffer.writeln("ID: ${widget.userId}");
      buffer.writeln("Meno: ${_userName ?? 'Unknown'}\n");

      buffer.writeln("Navštívené eventy (${visitedTitles.length}):");
      if (visitedTitles.isEmpty) {
        buffer.writeln("  - Žiadne");
      } else {
        for (var title in visitedTitles) {
          buffer.writeln("  - $title");
        }
      }
      buffer.writeln("");

      buffer.writeln("Obľúbené eventy (${favoriteTitles.length}):");
      if (favoriteTitles.isEmpty) {
        buffer.writeln("  - Žiadne");
      } else {
        for (var title in favoriteTitles) {
          buffer.writeln("  - $title");
        }
      }
      buffer.writeln("\n=====================================\n");

      final text = buffer.toString();

      //════════════════════════════════════════════════════
      //  WEB EXPORT – stiahne súbor v prehliadači
      //════════════════════════════════════════════════════
      if (kIsWeb) {
        web_download.downloadFile(text, "recommendations_export.txt");

        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text("📄 Súbor bol stiahnutý"))
        );
        return;
      }

      //════════════════════════════════════════════════════
      //  MOBIL / DESKTOP EXPORT
      //════════════════════════════════════════════════════
      final dir = await getApplicationDocumentsDirectory();
      final file = File("${dir.path}/recommendations_export.txt");
      await file.writeAsString(text);

      await Share.shareXFiles(
          [XFile(file.path)],
          subject: "Export odporúčaní",
          text: "Tu sú tvoje odporúčania"
      );

      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("📄 Súbor uložený a pripravený na zdieľanie"))
      );
    }
    catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Chyba pri exporte: $e"),
          backgroundColor: Colors.red,
        ),
      );
    }
  }






 /* Future<void> _exportResults() async {
    if (_recommendations.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Žiadne výsledky na export'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    try {
      // Vezmi top 5 eventov
      final topEvents = _recommendations.take(5).toList();

      // Vytvor textový obsah
      StringBuffer buffer = StringBuffer();

      // Header
      buffer.writeln('═══════════════════════════════════════════════════════');
      buffer.writeln('        EXPORT ODPORÚČANÍ - RECOMMENDATION SYSTEM');
      buffer.writeln('═══════════════════════════════════════════════════════');
      buffer.writeln();
      buffer.writeln('📅 Dátum exportu: ${DateFormat('d. MMMM yyyy, HH:mm').format(DateTime.now())}');
      buffer.writeln('👤 Užívateľ: ${_userName ?? widget.userId}');
      buffer.writeln('🎯 Počet odporúčaní: ${_recommendations.length}');
      buffer.writeln();

      // Aktuálne nastavenie váh
      buffer.writeln('─────────────────────────────────────────────────────');
      buffer.writeln('⚙️  AKTUÁLNE NASTAVENIE VÁH');
      buffer.writeln('─────────────────────────────────────────────────────');
      buffer.writeln('📂 Hlavná kategória:     ${(RecommendationEngine.MAIN_CATEGORY_WEIGHT * 100).toStringAsFixed(1)}%');
      buffer.writeln('📁 Podkategória:         ${(RecommendationEngine.SUB_CATEGORY_WEIGHT * 100).toStringAsFixed(1)}%');
      buffer.writeln('📍 Vzdialenosť:          ${(RecommendationEngine.DISTANCE_WEIGHT * 100).toStringAsFixed(1)}%');
      buffer.writeln('⭐ Rating:               ${(RecommendationEngine.RATING_WEIGHT * 100).toStringAsFixed(1)}%');
      buffer.writeln('👥 Popularita:           ${(RecommendationEngine.POPULARITY_WEIGHT * 100).toStringAsFixed(1)}%');
      buffer.writeln('💖 Obľúbený bonus:       ${(RecommendationEngine.FAVORITE_SUBCATEGORY_BONUS * 100).toStringAsFixed(1)}%');
      buffer.writeln();

      // Top 5 eventov
      buffer.writeln('═══════════════════════════════════════════════════════');
      buffer.writeln('        🏆 TOP 5 ODPORÚČANÝCH EVENTOV');
      buffer.writeln('═══════════════════════════════════════════════════════');
      buffer.writeln();

      for (int i = 0; i < topEvents.length; i++) {
        final scored = topEvents[i];
        final event = scored.event;
        final breakdown = scored.scoreBreakdown;
        final mainCategory = CategoryMapper.getMainCategory(event.category);

        buffer.writeln('┌─────────────────────────────────────────────────────┐');
        buffer.writeln('│ #${i + 1}. ${event.title}');
        buffer.writeln('├─────────────────────────────────────────────────────┤');
        buffer.writeln('│ 📊 CELKOVÉ SKÓRE: ${(scored.score * 100).toStringAsFixed(1)}%');
        buffer.writeln('│');
        buffer.writeln('│ 📋 ZÁKLADNÉ INFORMÁCIE:');
        buffer.writeln('│   • Kategória: $mainCategory / ${event.category}');
        buffer.writeln('│   • Dátum: ${DateFormat('d. MMM yyyy, HH:mm').format(event.date)}');
        buffer.writeln('│   • Vzdialenosť: ${breakdown['distance_km']?.toStringAsFixed(1)} km');
        buffer.writeln('│   • Rating: ${event.rating.toStringAsFixed(1)}/5.0 (${event.totalRatings} hodnotení)');
        buffer.writeln('│   • Účastníci: ${event.attendees.length}');
        buffer.writeln('│');
        buffer.writeln('│ 🔍 BREAKDOWN SKÓRE:');

        if (breakdown['main_category'] != null && breakdown['main_category']! > 0) {
          final matchPercent = (breakdown['main_category_match']! * 100).toStringAsFixed(1);
          final scorePercent = (breakdown['main_category']! * 100).toStringAsFixed(1);
          buffer.writeln('│   📂 Hlavná kategória:  $scorePercent% (zhoda: $matchPercent%)');
        }

        if (breakdown['sub_category'] != null && breakdown['sub_category']! > 0) {
          final matchPercent = (breakdown['sub_category_match']! * 100).toStringAsFixed(1);
          final scorePercent = (breakdown['sub_category']! * 100).toStringAsFixed(1);
          buffer.writeln('│   📁 Podkategória:      $scorePercent% (zhoda: $matchPercent%)');
        }

        if (breakdown['distance'] != null && breakdown['distance']! > 0) {
          final scorePercent = (breakdown['distance']! * 100).toStringAsFixed(1);
          final distanceKm = breakdown['distance_km']?.toStringAsFixed(1) ?? '?';
          buffer.writeln('│   📍 Vzdialenosť:       $scorePercent% ($distanceKm km)');
        }

        if (breakdown['rating'] != null && breakdown['rating']! > 0) {
          final scorePercent = (breakdown['rating']! * 100).toStringAsFixed(1);
          final ratingValue = breakdown['rating_value']?.toStringAsFixed(1) ?? '?';
          buffer.writeln('│   ⭐ Rating:            $scorePercent% ($ratingValue/5.0)');
        }

        if (breakdown['popularity'] != null && breakdown['popularity']! > 0) {
          final scorePercent = (breakdown['popularity']! * 100).toStringAsFixed(1);
          final attendees = breakdown['attendees_count']?.toInt() ?? 0;
          buffer.writeln('│   👥 Popularita:        $scorePercent% ($attendees účastníkov)');
        }

        if (breakdown['favorite_bonus'] != null && breakdown['favorite_bonus']! > 0) {
          final scorePercent = (breakdown['favorite_bonus']! * 100).toStringAsFixed(1);
          buffer.writeln('│   💖 Obľúbený bonus:    $scorePercent% ⭐');
        }

        buffer.writeln('└─────────────────────────────────────────────────────┘');
        buffer.writeln();
      }

      // Footer
      buffer.writeln('═══════════════════════════════════════════════════════');
      buffer.writeln('Vygenerované aplikáciou Event Recommendation System');
      buffer.writeln('═══════════════════════════════════════════════════════');

      // Ulož do súboru
      final directory = await getApplicationDocumentsDirectory();
      final timestamp = DateFormat('yyyy-MM-dd_HH-mm-ss').format(DateTime.now());
      final fileName = 'recommendations_export_$timestamp.txt';
      final file = File('${directory.path}/$fileName');

      await file.writeAsString(buffer.toString());

      // Zdieľaj súbor
      await Share.shareXFiles(
        [XFile(file.path)],
        subject: 'Export odporúčaní - $timestamp',
        text: 'Top 5 odporúčaných eventov pre ${_userName ?? widget.userId}',
      );

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('✅ Výsledky exportované do $fileName'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 3),
        ),
      );

    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ Chyba pri exporte: $e'),
          backgroundColor: Colors.red,
          duration: Duration(seconds: 3),
        ),
      );
    }
  }
*/
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
        actions: [
          // 🔥 Tlačidlo na export výsledkov
          IconButton(
            icon: Icon(Icons.file_download),
            tooltip: 'Exportovať výsledky',
            onPressed: _exportResults,
          ),
          // 🔥 Tlačidlo na nastavenie váh
          IconButton(
            icon: Icon(Icons.tune),
            tooltip: 'Nastaviť váhy',
            onPressed: () => _showWeightsDialog(),
          ),
        ],
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
        // Info banner s časom načítania
        _buildLoadTimeBanner(),

        // 🔥 NOVÉ: Info banner s váhami
        _buildWeightsBanner(),

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

  // 🔥 NOVÁ metóda: Banner s váhami
  Widget _buildWeightsBanner() {
    // Zoznam aktívnych váh
    List<String> activeWeights = [];

    if (RecommendationEngine.MAIN_CATEGORY_WEIGHT > 0) {
      activeWeights.add('Kategória ${(RecommendationEngine.MAIN_CATEGORY_WEIGHT * 100).toInt()}%');
    }
    if (RecommendationEngine.SUB_CATEGORY_WEIGHT > 0) {
      activeWeights.add('Podkat. ${(RecommendationEngine.SUB_CATEGORY_WEIGHT * 100).toInt()}%');
    }
    if (RecommendationEngine.DISTANCE_WEIGHT > 0) {
      activeWeights.add('Vzdialenosť ${(RecommendationEngine.DISTANCE_WEIGHT * 100).toInt()}%');
    }
    if (RecommendationEngine.RATING_WEIGHT > 0) {
      activeWeights.add('Rating ${(RecommendationEngine.RATING_WEIGHT * 100).toInt()}%');
    }
    if (RecommendationEngine.POPULARITY_WEIGHT > 0) {
      activeWeights.add('Popularita ${(RecommendationEngine.POPULARITY_WEIGHT * 100).toInt()}%');
    }
    if (RecommendationEngine.FAVORITE_SUBCATEGORY_BONUS > 0) {
      activeWeights.add('Bonus ⭐ ${(RecommendationEngine.FAVORITE_SUBCATEGORY_BONUS * 100).toInt()}%');
    }

    if (activeWeights.isEmpty) {
      activeWeights.add('Žiadne váhy nastavené');
    }

    return Container(
      width: double.infinity,
      padding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        border: Border(
          bottom: BorderSide(color: Colors.blue.shade200, width: 1),
        ),
      ),
      child: Wrap(
        alignment: WrapAlignment.center,
        spacing: 8,
        runSpacing: 4,
        children: [
          Icon(Icons.tune, size: 16, color: Colors.blue.shade700),
          ...activeWeights.map((w) => Text(
            w,
            style: TextStyle(
              color: Colors.blue.shade700,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          )).toList(),
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
              SizedBox(height: 4),
              // 🔥 Zobrazenie počtu účastníkov a FULL status
              _buildInfoRow(
                Icons.people,
                '${event.attendees.length}/${event.maxAttendees} účastníkov' +
                  (event.attendees.length >= event.maxAttendees ? ' - PLNÉ ❌' : ''),
                event.attendees.length >= event.maxAttendees ? Colors.red : Colors.green,
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

          // 🔥 DYNAMICKÉ ZOBRAZENIE: Použij váhy z RecommendationEngine
          // Zobraz len komponenty ktoré majú nenulovú váhu

          if (RecommendationEngine.MAIN_CATEGORY_WEIGHT > 0 && (breakdown['main_category'] ?? 0) > 0)
            _buildScoreRow(
              'Hlavná kategória',
              breakdown['main_category']!,
              breakdown['main_category_match'] ?? 0,
              Icons.category,
              Colors.purple,
            ),

          if (RecommendationEngine.SUB_CATEGORY_WEIGHT > 0 && (breakdown['sub_category'] ?? 0) > 0)
            _buildScoreRow(
              'Podkategória',
              breakdown['sub_category']!,
              breakdown['sub_category_match'] ?? 0,
              Icons.category_outlined,
              Colors.deepPurple,
            ),

          if (RecommendationEngine.DISTANCE_WEIGHT > 0 && (breakdown['distance'] ?? 0) > 0)
            _buildScoreRow(
              'Vzdialenosť',
              breakdown['distance']!,
              breakdown['distance']! / RecommendationEngine.DISTANCE_WEIGHT, // 🔥 Použij váhu
              Icons.location_on,
              Colors.blue,
            ),

          if (RecommendationEngine.RATING_WEIGHT > 0 && (breakdown['rating'] ?? 0) > 0)
            _buildScoreRow(
              'Rating',
              breakdown['rating']!,
              breakdown['rating_value']! / 5.0,
              Icons.star,
              Colors.amber,
            ),

          if (RecommendationEngine.POPULARITY_WEIGHT > 0 && (breakdown['popularity'] ?? 0) > 0)
            _buildScoreRow(
              'Popularita',
              breakdown['popularity']!,
              breakdown['attendees_count']! / 100,
              Icons.people,
              Colors.green,
            ),

          if (RecommendationEngine.FAVORITE_SUBCATEGORY_BONUS > 0 && (breakdown['favorite_bonus'] ?? 0) > 0)
            _buildScoreRow(
              'Obľúbený bonus ⭐',
              breakdown['favorite_bonus']!,
              breakdown['favorite_bonus']! / RecommendationEngine.FAVORITE_SUBCATEGORY_BONUS, // 🔥 Použij váhu
              Icons.favorite,
              Colors.pink,
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

  // 🔥 NOVÁ metóda: Dialog na nastavenie váh
  void _showWeightsDialog() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return _WeightsDialog(
          onApply: () {
            // Refresh odporúčania po zmene váh
            _loadRecommendations();
          },
        );
      },
    );
  }
}

// 🔥 NOVÝ StatefulWidget: Dialog s váhami
class _WeightsDialog extends StatefulWidget {
  final VoidCallback onApply;

  const _WeightsDialog({required this.onApply});

  @override
  _WeightsDialogState createState() => _WeightsDialogState();
}

class _WeightsDialogState extends State<_WeightsDialog> {
  late double mainCategoryWeight;
  late double subCategoryWeight;
  late double distanceWeight;
  late double ratingWeight;
  late double popularityWeight;
  late double favoriteBonus;

  @override
  void initState() {
    super.initState();
    // Načítaj aktuálne váhy
    mainCategoryWeight = RecommendationEngine.MAIN_CATEGORY_WEIGHT;
    subCategoryWeight = RecommendationEngine.SUB_CATEGORY_WEIGHT;
    distanceWeight = RecommendationEngine.DISTANCE_WEIGHT;
    ratingWeight = RecommendationEngine.RATING_WEIGHT;
    popularityWeight = RecommendationEngine.POPULARITY_WEIGHT;
    favoriteBonus = RecommendationEngine.FAVORITE_SUBCATEGORY_BONUS;
  }

  double get totalWeight =>
      mainCategoryWeight +
      subCategoryWeight +
      distanceWeight +
      ratingWeight +
      popularityWeight +
      favoriteBonus;

  // 🔥 NOVÁ metóda: Prerozdelí váhy proporčne keď používateľ zmení jednu váhu
  void _adjustWeight(String weightName, double newValue) {
    // Clamp new value to valid range
    newValue = newValue.clamp(0.0, 1.0);

    // Získaj starú hodnotu
    double oldValue = _getWeight(weightName);

    // Vypočítaj delta (koľko sa zmenilo)
    double delta = newValue - oldValue;

    // Ak je delta 0, nič nerob
    if (delta.abs() < 0.001) return;

    // Získaj zoznam ostatných váh
    List<String> otherWeights = ['main', 'sub', 'distance', 'rating', 'popularity', 'favorite']
      ..remove(weightName);

    // Vypočítaj súčet ostatných váh
    double sumOfOthers = 0;
    for (var name in otherWeights) {
      sumOfOthers += _getWeight(name);
    }

    // Ak sú všetky ostatné váhy 0, rovnomerne rozdeľ
    if (sumOfOthers < 0.001) {
      double remaining = 1.0 - newValue;
      double perWeight = remaining / otherWeights.length;

      setState(() {
        _setWeight(weightName, newValue);
        for (var name in otherWeights) {
          _setWeight(name, perWeight);
        }
      });
      return;
    }

    // 🔥 Proporčne prerozdelí delta medzi ostatné váhy
    // Každá váha dostane podiel úmerný jej súčasnej hodnote
    Map<String, double> newWeights = {};
    double remainingToDistribute = -delta; // Koľko treba rozdeliť medzi ostatné

    // Prvý priechod: proporčne rozdeľ
    for (var name in otherWeights) {
      double currentWeight = _getWeight(name);
      double proportion = currentWeight / sumOfOthers;
      double adjustment = remainingToDistribute * proportion;
      double newWeight = currentWeight + adjustment;
      newWeights[name] = newWeight;
    }

    // Druhý priechod: oprav záporné hodnoty
    bool hasNegative = true;
    int maxIterations = 10;
    int iteration = 0;

    while (hasNegative && iteration < maxIterations) {
      hasNegative = false;
      double excessToRedistribute = 0;
      List<String> positiveWeights = [];

      // Nájdi záporné váhy a pozitívne váhy
      for (var name in otherWeights) {
        if (newWeights[name]! < 0) {
          excessToRedistribute += newWeights[name]!.abs();
          newWeights[name] = 0;
          hasNegative = true;
        } else if (newWeights[name]! > 0) {
          positiveWeights.add(name);
        }
      }

      // Prerozdelí prebytok medzi pozitívne váhy
      if (hasNegative && positiveWeights.isNotEmpty) {
        double sumPositive = 0;
        for (var name in positiveWeights) {
          sumPositive += newWeights[name]!;
        }

        if (sumPositive > 0) {
          for (var name in positiveWeights) {
            double proportion = newWeights[name]! / sumPositive;
            newWeights[name] = newWeights[name]! - (excessToRedistribute * proportion);
          }
        }
      }

      iteration++;
    }

    // Aplikuj zmeny
    setState(() {
      _setWeight(weightName, newValue);
      newWeights.forEach((name, value) {
        _setWeight(name, value.clamp(0.0, 1.0));
      });
    });
  }

  double _getWeight(String name) {
    switch (name) {
      case 'main':
        return mainCategoryWeight;
      case 'sub':
        return subCategoryWeight;
      case 'distance':
        return distanceWeight;
      case 'rating':
        return ratingWeight;
      case 'popularity':
        return popularityWeight;
      case 'favorite':
        return favoriteBonus;
      default:
        return 0;
    }
  }

  void _setWeight(String name, double value) {
    switch (name) {
      case 'main':
        mainCategoryWeight = value;
        break;
      case 'sub':
        subCategoryWeight = value;
        break;
      case 'distance':
        distanceWeight = value;
        break;
      case 'rating':
        ratingWeight = value;
        break;
      case 'popularity':
        popularityWeight = value;
        break;
      case 'favorite':
        favoriteBonus = value;
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(Icons.tune, color: Colors.deepPurple),
          SizedBox(width: 8),
          Text('Nastavenie váh'),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green.shade200),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.check_circle, color: Colors.green.shade700, size: 20),
                  SizedBox(width: 8),
                  Text(
                    'Celková suma: ${(totalWeight * 100).toStringAsFixed(1)}%',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: Colors.green.shade700,
                    ),
                  ),
                ],
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Slidery sú prepojené - úprava jednej váhy automaticky prerozdelí ostatné',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 12,
                fontStyle: FontStyle.italic,
              ),
            ),
            SizedBox(height: 16),

            _buildWeightSlider(
              '📂 Hlavná kategória',
              mainCategoryWeight,
              (val) => _adjustWeight('main', val),
              Colors.purple,
            ),
            _buildWeightSlider(
              '📁 Podkategória',
              subCategoryWeight,
              (val) => _adjustWeight('sub', val),
              Colors.deepPurple,
            ),
            _buildWeightSlider(
              '📍 Vzdialenosť',
              distanceWeight,
              (val) => _adjustWeight('distance', val),
              Colors.blue,
            ),
            _buildWeightSlider(
              '⭐ Rating',
              ratingWeight,
              (val) => _adjustWeight('rating', val),
              Colors.amber,
            ),
            _buildWeightSlider(
              '👥 Popularita',
              popularityWeight,
              (val) => _adjustWeight('popularity', val),
              Colors.green,
            ),
            _buildWeightSlider(
              '💖 Obľúbený bonus',
              favoriteBonus,
              (val) => _adjustWeight('favorite', val),
              Colors.pink,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () {
            // Reset na default
            RecommendationEngine.resetWeights();
            Navigator.pop(context);
            widget.onApply();
          },
          child: Text('Reset'),
        ),
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text('Zrušiť'),
        ),
        ElevatedButton(
          onPressed: () {
            // Aplikuj nové váhy
            RecommendationEngine.MAIN_CATEGORY_WEIGHT = mainCategoryWeight;
            RecommendationEngine.SUB_CATEGORY_WEIGHT = subCategoryWeight;
            RecommendationEngine.DISTANCE_WEIGHT = distanceWeight;
            RecommendationEngine.RATING_WEIGHT = ratingWeight;
            RecommendationEngine.POPULARITY_WEIGHT = popularityWeight;
            RecommendationEngine.FAVORITE_SUBCATEGORY_BONUS = favoriteBonus;

            Navigator.pop(context);
            widget.onApply();
          },
          child: Text('Aplikovať'),
        ),
      ],
    );
  }

  Widget _buildWeightSlider(
    String label,
    double value,
    ValueChanged<double> onChanged,
    Color color,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: TextStyle(fontWeight: FontWeight.w500),
            ),
            Text(
              '${(value * 100).toInt()}%',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
        Slider(
          value: value,
          min: 0.0,
          max: 1.0,
          divisions: 20,
          activeColor: color,
          onChanged: onChanged,
        ),
        SizedBox(height: 8),
      ],
    );
  }
}
