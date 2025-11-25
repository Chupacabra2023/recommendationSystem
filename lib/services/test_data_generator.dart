import 'package:cloud_firestore/cloud_firestore.dart';
import '/models/recommendation_models.dart';
import 'dart:math';

class TestDataGenerator {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final Random _random = Random();

  // Bratislava coordinates
  final double bratislavaLat = 48.1486;
  final double bratislavaLng = 17.1077;

  // Main category map (group → subcategories)
  final Map<String, List<String>> categoryMap = {
    "Sports": [
      "Ball sports",
      "Athletics",
      "Combat sports",
      "Aquatic sports",
      "Gymnastics",
      "Cycling sports",
      "Winter sports",
      "Strength & Conditioning",
      "Outdoor sports",
      "Motor sports",
      "E-sports (competitive gaming)",
      "Racquet sports",
      "Watercraft sports",
      "Animal sports",
      "Extreme sports",
      "Team sports",
      "Individual sports",
      "Fitness & Wellness",
      "Precision sports",
      "Recreational sports"
    ],

    "Music & Entertainment": [
      "Koncert",
      "Festival",
      "Party / Clubbing",
      "Karaoke",
      "DJ Set",
      "Iný koncert"
    ],

    "Art & Culture": [
      "Film",
      "Divadlo",
      "Výstava",
      "Múzeum",
      "Literatúra / čítanie",
      "Maľovanie / kreatívne umenie",
      "Verejné zhromaždenie",
      "Protest"
    ],

    "Food & Drinks": [
      "Food festival",
      "Street food",
      "Degustácia vín",
      "Degustácia piva",
      "Reštauračné eventy",
      "Grilovačka",
      "Opekačka"
    ],

    "Business & Tech": [
      "Startup meetup",
      "Networking event",
      "Konferencia",
      "Prednáška",
      "Pitch Night",
      "Veľtrh práce",
      "Workshop (IT)",
      "Hackathon",
      "Gaming turnaj",
      "E-sports",
      "Odborné prednášky"
    ],

    "Education": [
      "Vzdelávací kurz",
      "Workshop (ručné práce)",
      "Jazykový kurz",
      "Osobný rozvoj",
      "Tvorivé dielne"
    ],

    "Nature & Outdoor": [
      "Turistika",
      "Výlet",
      "Kempovanie",
      "Návšteva parku",
      "Botanická záhrada"
    ],

    "Family & Kids": [
      "Rodinná akcia",
      "Tvorivé dielne pre deti",
      "Detské divadlo"
    ],

    "Community & Social": [
      "Speed dating",
      "Komunitné akcie",
      "Street meetup"
    ]
  };

  // FLAT LIST — toto opravuje undefined error
  late final List<String> categories =
  categoryMap.values.expand((x) => x).toList();

  final List<String> eventTitles = [
    'udalost 1'
        'udalost 2'
        'udalost 3'
        'udalost 4'
        'udalost 5'
        'udalost 6'
        'udalost 7'
        'udalost 8'
        'udalost 9'
        'udalost 10'
        'udalost 11'
        'udalost 12'
        'udalost 13'
        'udalost 14'
        'udalost 15'
  ];

  // ============================================================
  // Generate Users
  // ============================================================

  Future<void> generateTestUsers(int count) async {
    print('🔄 Generujem $count užívateľov...');

    for (int i = 0; i < count; i++) {
      final userId = 'test_user_$i';

      final lat = bratislavaLat + (_random.nextDouble() - 0.5) * 0.2;
      final lng = bratislavaLng + (_random.nextDouble() - 0.5) * 0.2;

      final visitedCount = 3 + _random.nextInt(8);
      final visitedIds = List.generate(
        visitedCount,
            (j) => 'test_event_${_random.nextInt(30)}',
      );

      final user = UserProfile(
        id: userId,
        name: 'Test User $i',
        location: GeoPoint(lat, lng),
        maxDistanceKm: 50,
        visitedEventIds: visitedIds,
      );

      await _firestore.collection('users').doc(userId).set(user.toJson());

      if ((i + 1) % 10 == 0) {
        print('👤 Vytvorených ${i + 1}/$count užívateľov');
      }
    }

    print('✅ Hotovo! Vytvorených $count užívateľov');
  }

  // ============================================================
  // Generate Events
  // ============================================================

  Future<void> generateTestEvents(int count) async {
    print('🔄 Generujem $count udalostí...');

    for (int i = 0; i < count; i++) {
      final eventId = 'test_event_$i';

      final lat = bratislavaLat + (_random.nextDouble() - 0.5) * 0.3;
      final lng = bratislavaLng + (_random.nextDouble() - 0.5) * 0.3;

      final category = categories[_random.nextInt(categories.length)];

      final daysAhead = 1 + _random.nextInt(30);
      final date = DateTime.now().add(Duration(days: daysAhead));

      final attendeeCount = _random.nextInt(51);
      final attendees = List.generate(
        attendeeCount,
            (j) => 'test_user_${_random.nextInt(100)}',
      );

      final rating = 3.0 + _random.nextDouble() * 2.0;
      final totalRatings = _random.nextInt(20) + 1;

      final event = Event(
        id: eventId,
        title: '${eventTitles[i % eventTitles.length]} #$i',
        category: category,
        location: GeoPoint(lat, lng),
        date: date,
        attendees: attendees,
        rating: rating,
        totalRatings: totalRatings,
        testDistanceKm: _random.nextInt(60) + 1,
      );

      await _firestore.collection('events').doc(eventId).set(event.toJson());

      if ((i + 1) % 10 == 0) {
        print('🎉 Vytvorených ${i + 1}/$count udalostí');
      }
    }

    print('✅ Hotovo! Vytvorených $count udalostí');
  }

  // ============================================================
  // Clear Data
  // ============================================================

  Future<void> clearTestData() async {
    print('🗑️ Mažem testovacie dáta...');

    final users = await _firestore
        .collection('users')
        .where(FieldPath.documentId, isGreaterThanOrEqualTo: 'test_user_')
        .where(FieldPath.documentId, isLessThan: 'test_user_\uf8ff')
        .get();

    for (var doc in users.docs) {
      await doc.reference.delete();
    }

    final events = await _firestore
        .collection('events')
        .where(FieldPath.documentId, isGreaterThanOrEqualTo: 'test_event_')
        .where(FieldPath.documentId, isLessThan: 'test_event_\uf8ff')
        .get();

    for (var doc in events.docs) {
      await doc.reference.delete();
    }

    print('✅ Testovacie dáta vymazané');
  }
}
