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
    'udalost 1',
        'udalost 2',
        'udalost 3',
        'udalost 4',
        'udalost 5',
        'udalost 6',
        'udalost 7',
        'udalost 8',
        'udalost 9',
        'udalost 10',
        'udalost 11',
        'udalost 12',
        'udalost 13',
        'udalost 14',
        'udalost 15',
  ];

  // ============================================================
  // Generate Users
  // ============================================================

  Future<void> generateTestUsers(int count) async {
    print('🔄 Generujem $count užívateľov...');

    // 1. Najprv načítaj všetky existujúce test eventy
    final eventsSnapshot = await _firestore
        .collection('events')
        .where(FieldPath.documentId, isGreaterThanOrEqualTo: 'test_event_')
        .where(FieldPath.documentId, isLessThan: 'test_event_\uf8ff')
        .get();

    if (eventsSnapshot.docs.isEmpty) {
      print('⚠️ Žiadne test eventy v databáze! Najprv spusti generateTestEvents()');
      return;
    }

    final availableEventIds = eventsSnapshot.docs.map((doc) => doc.id).toList();
    print('📦 Našiel som ${availableEventIds.length} existujúcich eventov');

    int totalAttempts = 0;
    int successfulAdds = 0;
    int capacityReached = 0;

    for (int i = 0; i < count; i++) {
      final userId = 'test_user_$i';

      final lat = bratislavaLat + (_random.nextDouble() - 0.5) * 0.2;
      final lng = bratislavaLng + (_random.nextDouble() - 0.5) * 0.2;

      // 2. Vyber náhodné eventy pre návštevu (3-10)
      final visitedCount = 3 + _random.nextInt(8);
      final shuffled = List<String>.from(availableEventIds)..shuffle(_random);
      final visitedIds = shuffled.take(visitedCount.clamp(0, availableEventIds.length)).toList();

      // 3. 🔥 OPRAVA: Obľúbené vyber IBA z navštívených (0-5)
      final favoriteCount = _random.nextInt(6).clamp(0, visitedIds.length); // max 5 alebo počet visited
      final shuffledVisited = List<String>.from(visitedIds)..shuffle(_random);
      final favoriteIds = shuffledVisited.take(favoriteCount).toList();

      final user = UserProfile(
        id: userId,
        name: 'Test User $i',
        location: GeoPoint(lat, lng),
        maxDistanceKm: 50,
        visitedEventIds: visitedIds,
        favoriteEventIds: favoriteIds,
      );

      await _firestore.collection('users').doc(userId).set(user.toJson());

      // 4. 🔥 OPRAVA: Pridaj používateľa do attendees každého navštíveného eventu
      // ⚠️ KONTROLA KAPACITY: pridaj len ak nie je event plný
      for (String eventId in visitedIds) {
        totalAttempts++;
        try {
          // Načítaj aktuálny stav eventu
          final eventDoc = await _firestore.collection('events').doc(eventId).get();
          if (eventDoc.exists) {
            final eventData = eventDoc.data()!;
            final currentAttendees = (eventData['attendees'] as List<dynamic>?) ?? [];
            final maxAttendees = eventData['maxAttendees'] as int? ?? 100;

            // Pridaj len ak je voľné miesto
            if (currentAttendees.length < maxAttendees) {
              await _firestore.collection('events').doc(eventId).update({
                'attendees': FieldValue.arrayUnion([userId])
              });
              successfulAdds++;
            } else {
              capacityReached++;
            }
          }
        } catch (e) {
          print('⚠️ Chyba pri pridávaní užívateľa do eventu $eventId: $e');
        }
      }

      if ((i + 1) % 10 == 0) {
        print('👤 Vytvorených ${i + 1}/$count užívateľov');
      }
    }

    print('✅ Hotovo! Vytvorených $count užívateľov');
    print('   (každý má 3-10 navštívených eventov a 0-5 obľúbených z navštívených)');
    print('📊 Štatistika kapacity eventov:');
    print('   • Pokusov o pridanie: $totalAttempts');
    print('   • Úspešne pridaných: $successfulAdds');
    print('   • Odmietnutých (plná kapacita): $capacityReached');
    if (totalAttempts > 0) {
      final successRate = (successfulAdds / totalAttempts * 100).toStringAsFixed(1);
      print('   • Úspešnosť: $successRate%');
    }
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

      // 🔥 OPRAVA: Attendees sa budú pridávať cez generateTestUsers()
      final attendees = <String>[];

      final rating = 3.0 + _random.nextDouble() * 2.0;
      final totalRatings = _random.nextInt(20) + 1;

      // 🔥 Random maxAttendees od 4 do 100
      final maxAttendees = 4 + _random.nextInt(97); // 4 až 100

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
        maxAttendees: maxAttendees, // 🔥 Random od 4 do 100
      );

      await _firestore.collection('events').doc(eventId).set(event.toJson());

      if ((i + 1) % 10 == 0) {
        print('🎉 Vytvorených ${i + 1}/$count udalostí');
      }
    }

    print('✅ Hotovo! Vytvorených $count udalostí');
    print('   (attendees sa pridajú pri generovaní užívateľov)');
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
