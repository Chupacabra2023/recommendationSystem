import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/recommendation_models.dart';
import '../utils/category_mapper.dart';
import 'recommendation_service.dart';
import 'dart:math';

class RecommendationEngine implements RecommendationService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  // Váhy pre scoring - 🔥 Hlavná kategória 20%, ostatné 16%
  static double MAIN_CATEGORY_WEIGHT = 0.20;
  static double SUB_CATEGORY_WEIGHT = 0.16;
  static double DISTANCE_WEIGHT = 0.16;
  static double RATING_WEIGHT = 0.16;
  static double POPULARITY_WEIGHT = 0.16;
  static double FAVORITE_SUBCATEGORY_BONUS = 0.16;

  // 🔥 Reset váh na default (hlavná kategória 20%, ostatné 16%)
  static void resetWeights() {
    MAIN_CATEGORY_WEIGHT = 0.20;
    SUB_CATEGORY_WEIGHT = 0.16;
    DISTANCE_WEIGHT = 0.16;
    RATING_WEIGHT = 0.16;
    POPULARITY_WEIGHT = 0.16;
    FAVORITE_SUBCATEGORY_BONUS = 0.16;
  }

  // ════════════════════════════════════════════════════════════
  // IMPLEMENTÁCIA: getUserProfile (s hlavnými + podkategóriami)
  // ════════════════════════════════════════════════════════════

  @override
  Future<Map<String, double>> getUserProfile(String userId) async {
    print('📊 Počítam profil pre užívateľa $userId...');

    try {
      // 1. Načítaj užívateľa
      final userDoc = await _firestore.collection('users').doc(userId).get();

      if (!userDoc.exists) {
        print('❌ Užívateľ $userId neexistuje');
        return {};
      }

      final user = UserProfile.fromJson(userDoc.data()!, userId);

      // 2. Ak nemá žiadne navštívené eventy
      if (user.visitedEventIds.isEmpty) {
        print('ℹ️ Užívateľ ešte nenavštívil žiadne eventy');
        return _getDefaultProfile();
      }

      // 3. Načítaj všetky navštívené eventy a mapuj kategórie
      // 🔥 DÔLEŽITÉ: Obľúbené sa NEPOČÍTAJÚ do preferencií!
      // Obľúbené sa používajú len pre bonus pri skórovaní.
      Map<String, int> mainCategoryCounts = {};
      Map<String, int> subCategoryCounts = {};
      int totalEvents = 0;

      for (String eventId in user.visitedEventIds) {
        try {
          final eventDoc = await _firestore
              .collection('events')
              .doc(eventId)
              .get();

          if (eventDoc.exists) {
            final event = Event.fromJson(eventDoc.data()!, eventId);

            // Hlavná kategória
            String mainCategory = CategoryMapper.getMainCategory(event.category);
            mainCategoryCounts[mainCategory] =
                (mainCategoryCounts[mainCategory] ?? 0) + 1;

            // Podkategória (originálna)
            subCategoryCounts[event.category] =
                (subCategoryCounts[event.category] ?? 0) + 1;

            totalEvents++;
          }
        } catch (e) {
          print('⚠️ Chyba pri načítaní eventu $eventId: $e');
        }
      }

      // 4. Prepočítaj na percentá (0.0 - 1.0)
      Map<String, double> preferences = {};

      if (totalEvents > 0) {
        // Hlavné kategórie
        mainCategoryCounts.forEach((category, count) {
          preferences[category] = count / totalEvents;
        });

        // Podkategórie
        subCategoryCounts.forEach((subCategory, count) {
          preferences[subCategory] = count / totalEvents;
        });
      }

      print('✅ Profil vypočítaný (IBA z navštívených):');
      print('   Navštívené eventy: ${user.visitedEventIds.length}');
      print('   Obľúbené eventy: ${user.favoriteEventIds.length} (používajú sa len pre bonus)');
      print('   Hlavné kategórie: ${mainCategoryCounts.length}');
      print('   Podkategórie: ${subCategoryCounts.length}');
      print('📊 CELÝ userProfile:');
      preferences.forEach((key, value) {
        print('   "$key": ${(value * 100).toStringAsFixed(1)}%');
      });
      print('   SÚČET: ${(preferences.values.fold(0.0, (a, b) => a + b) * 100).toStringAsFixed(1)}%');


      // Debug výpis hlavných kategórií
      mainCategoryCounts.forEach((cat, count) {
        print('   $cat: ${(preferences[cat]! * 100).toStringAsFixed(1)}%');
      });

      return preferences;

    } catch (e) {
      print('❌ Chyba pri výpočte profilu: $e');
      return {};
    }
  }

  /// Defaultný profil pre nových užívateľov (prázdny = všetky rovnaké)
  Map<String, double> _getDefaultProfile() {
    return {};
  }

  // ════════════════════════════════════════════════════════════
  // HELPER: Výpočet vzdialenosti (Haversine formula)
  // ════════════════════════════════════════════════════════════

  double _calculateDistance(GeoPoint point1, GeoPoint point2) {
    const double earthRadius = 6371; // km

    double lat1 = point1.latitude * pi / 180;
    double lat2 = point2.latitude * pi / 180;
    double dLat = (point2.latitude - point1.latitude) * pi / 180;
    double dLng = (point2.longitude - point1.longitude) * pi / 180;

    double a = sin(dLat / 2) * sin(dLat / 2) +
        cos(lat1) * cos(lat2) *
            sin(dLng / 2) * sin(dLng / 2);

    double c = 2 * atan2(sqrt(a), sqrt(1 - a));

    return earthRadius * c;
  }

  // ════════════════════════════════════════════════════════════
  // CORE: Skóruj jeden event (hlavná + podkategória)
  // ════════════════════════════════════════════════════════════

  ScoredEvent _scoreEvent({
    required Event event,
    required UserProfile user,
    required Map<String, double> userProfile,
    required Set<String> favoriteSubCategories, // 🔥
  }) {

    // Už bol na tomto evente? Skip.
    if (user.visitedEventIds.contains(event.id)) {
      return ScoredEvent(
        event: event,
        score: -1,
        scoreBreakdown: {'already_visited': -1},
      );
    }

    // Event je v minulosti? Skip.
    if (event.date.isBefore(DateTime.now())) {
      return ScoredEvent(
        event: event,
        score: -1,
        scoreBreakdown: {'past_event': -1},
      );
    }

    // Event je plný? Skip.
    if (event.attendees.length >= event.maxAttendees) {
      return ScoredEvent(
        event: event,
        score: -1,
        scoreBreakdown: {'event_full': -1},
      );
    }

    Map<String, double> breakdown = {};

    // Konvertuj podkategóriu eventu na hlavnú
    String mainCategory = CategoryMapper.getMainCategory(event.category);
    String subCategory = event.category;

    breakdown['main_category_name'] = mainCategory.hashCode.toDouble();
    breakdown['sub_category_name'] = subCategory.hashCode.toDouble();

    // ────────────────────────────────────────────────────────
    // 1️⃣ HLAVNÁ KATEGÓRIA
    // ────────────────────────────────────────────────────────
    double mainCategoryMatch = userProfile[mainCategory] ?? 0.0;

    // Pre nových užívateľov (bez preferencií) dáme všetkým rovnakú šancu
    if (userProfile.isEmpty) {
      mainCategoryMatch = 0.5; // 50% - neutrálne
    } else if (mainCategoryMatch == 0.0) {
      // Užívateľ túto kategóriu ešte nenavštívil → malá šanca
      mainCategoryMatch = 0.05; // 5%
    }

    double mainCategoryScore = mainCategoryMatch * MAIN_CATEGORY_WEIGHT;
    breakdown['main_category'] = mainCategoryScore;
    breakdown['main_category_match'] = mainCategoryMatch;

    // ────────────────────────────────────────────────────────
    // 2️⃣ PODKATEGÓRIA - ─────────────────
    double subCategoryMatch = userProfile[subCategory] ?? 0.0;
    double subCategoryScore = subCategoryMatch * SUB_CATEGORY_WEIGHT;

    breakdown['sub_category'] = subCategoryScore;
    breakdown['sub_category_match'] = subCategoryMatch;

    // ────────────────────────────────────────────────────────
    // 3️⃣ VZDIALENOSŤ
    // ────────────────────────────────────────────────────────
    double distance = _calculateDistance(user.location, event.location);

    // Normalizácia: bližšie = lepšie skóre
    // Formula: 1 / (1 + distance/10)
    // Príklady: 0km = 1.0, 5km = 0.66, 10km = 0.5, 20km = 0.33
    double distanceScore = 1 / (1 + distance / 10);
    distanceScore = distanceScore * DISTANCE_WEIGHT;

    breakdown['distance'] = distanceScore;
    breakdown['distance_km'] = distance;

    // ────────────────────────────────────────────────────────
    // 4️⃣ RATING (10% váha) - 🔥 ZNÍŽENÉ z 20% na 10%
    // ────────────────────────────────────────────────────────
    double ratingScore = 0.0;

    if (event.totalRatings > 0) {
      // Má hodnotenia → použi ich
      ratingScore = (event.rating / 5.0) * RATING_WEIGHT;
    } else {
      // Nový event → daj mu priemerné skóre
      ratingScore = 0.5 * RATING_WEIGHT; // Neutrálne
    }

    breakdown['rating'] = ratingScore;
    breakdown['rating_value'] = event.rating;

    // ────────────────────────────────────────────────────────
    // 5️⃣ POPULARITA (10% váha)
    // ────────────────────────────────────────────────────────
    // Normalizácia: 0-100 účastníkov → 0.0-1.0
    // Potrebujete mať v Event modeli aj maxCapacity
    double popularityScore = min(event.attendees.length / event.maxAttendees, 1.0);
    popularityScore = popularityScore * POPULARITY_WEIGHT;

    breakdown['popularity'] = popularityScore;
    breakdown['attendees_count'] = event.attendees.length.toDouble();

    // ────────────────────────────────────────────────────────
    // 6️⃣ BONUS: Event má rovnakú sub-kategóriu ako obľúbené 🔥 NOVÉ
    // ────────────────────────────────────────────────────────
    double favoriteBonus = 0.0;
    if (favoriteSubCategories.contains(subCategory)) {
      favoriteBonus = FAVORITE_SUBCATEGORY_BONUS;
      breakdown['favorite_bonus'] = favoriteBonus;
    }

    // ────────────────────────────────────────────────────────
    // CELKOVÉ SKÓRE (40% + 10% + 30% + 10% + 10% + bonus)
    // ────────────────────────────────────────────────────────
    double totalScore =
        mainCategoryScore +
            subCategoryScore +     // 🔥 NOVÉ
            distanceScore +
            ratingScore +
            popularityScore +
            favoriteBonus;         // 🔥 NOVÉ

    print('🔍 DEBUG: ${event.title}');
    print('   Kategória: $subCategory → $mainCategory');
    print('   mainCategoryMatch: $mainCategoryMatch');
    print('   userProfile keys: ${userProfile.keys.toList()}');
    print('   userProfile[Sports]: ${userProfile["Sports"]}');
    print('   Vzdialenosť: ${breakdown["distance_km"]} km');
    print('   SKÓRE: $totalScore');
    print('✅ Profil vypočítaný (IBA z navštívených):');



    return ScoredEvent(
      event: event,
      score: totalScore,
      scoreBreakdown: breakdown,
    );
  }

  // ════════════════════════════════════════════════════════════
  // IMPLEMENTÁCIA: getRecommendations
  // ════════════════════════════════════════════════════════════

  @override
  Future<List<ScoredEvent>> getRecommendations({
    required String userId,
    int count = 10,
    int maxDistanceKm = 50,
  }) async {

    print('🎯 Hľadám odporúčania pre $userId...');

    try {
      // ────────────────────────────────────────────────────────
      // 1. Načítaj užívateľa
      // ────────────────────────────────────────────────────────
      final userDoc = await _firestore.collection('users').doc(userId).get();

      if (!userDoc.exists) {
        throw Exception('Užívateľ $userId neexistuje');
      }

      final user = UserProfile.fromJson(userDoc.data()!, userId);
      print('👤 Užívateľ: ${user.name}');
      print('📍 Lokácia: ${user.location.latitude}, ${user.location.longitude}');
      print('📚 Navštívené eventy: ${user.visitedEventIds.length}');
      print('⭐ Obľúbené eventy: ${user.favoriteEventIds.length}'); // 🔥 NOVÉ

      // Debug výpis celého userProfile


      // ────────────────────────────────────────────────────────
      // 2. Načítaj sub-kategórie obľúbených eventov 🔥 NOVÉ
      // ────────────────────────────────────────────────────────
      Set<String> favoriteSubCategories = {};

      for (String eventId in user.favoriteEventIds) {
        try {
          final eventDoc = await _firestore
              .collection('events')
              .doc(eventId)
              .get();

          if (eventDoc.exists) {
            final event = Event.fromJson(eventDoc.data()!, eventId);
            favoriteSubCategories.add(event.category);
          }
        } catch (e) {
          print('⚠️ Chyba pri načítaní obľúbeného eventu $eventId: $e');
        }
      }

      print('🎯 Obľúbené sub-kategórie: $favoriteSubCategories');

      // ────────────────────────────────────────────────────────
      // 3. Vypočítaj užívateľský profil (hlavné + podkategórie)
      // ────────────────────────────────────────────────────────
      final userProfile = await getUserProfile(userId);

      // ────────────────────────────────────────────────────────
      // 3. Načítaj všetky budúce eventy
      // ────────────────────────────────────────────────────────
      final eventsSnapshot = await _firestore
          .collection('events')
          .where('date', isGreaterThan: Timestamp.now())
          .get();

      print('📦 Načítaných ${eventsSnapshot.docs.length} budúcich eventov');

      // ────────────────────────────────────────────────────────
      // 4. Skóruj každý event
      // ────────────────────────────────────────────────────────
      List<ScoredEvent> scoredEvents = [];
      int visitedCount = 0;
      int pastCount = 0;
      int fullCount = 0;
      int tooFarCount = 0;

      for (var doc in eventsSnapshot.docs) {
        final event = Event.fromJson(doc.data(), doc.id);

        final scored = _scoreEvent(
          event: event,
          user: user,
          userProfile: userProfile,
          favoriteSubCategories: favoriteSubCategories, // 🔥 NOVÉ
        );

        // Počítaj dôvody filtrovania
        if (scored.scoreBreakdown.containsKey('already_visited')) {
          visitedCount++;
        } else if (scored.scoreBreakdown.containsKey('past_event')) {
          pastCount++;
        } else if (scored.scoreBreakdown.containsKey('event_full')) {
          fullCount++;
        } else if (scored.score > 0) {
          // Filter: Max vzdialenosť
          double distance = scored.scoreBreakdown['distance_km'] ?? 999;

          if (distance <= maxDistanceKm) {
            scoredEvents.add(scored);
          } else {
            tooFarCount++;
          }
        }
      }

      print('✅ Skórovaných ${scoredEvents.length} eventov');
      print('🚫 Vyfiltrované:');
      print('   • Už navštívené: $visitedCount');
      print('   • Minulé: $pastCount');
      print('   • Plné (bez voľných miest): $fullCount');
      print('   • Príliš ďaleko: $tooFarCount');

      // ────────────────────────────────────────────────────────
      // 5. Zoradi od najvyššieho skóre
      // ────────────────────────────────────────────────────────
      scoredEvents.sort((a, b) => b.score.compareTo(a.score));

      // ────────────────────────────────────────────────────────
      // 6. Vráť TOP N
      // ────────────────────────────────────────────────────────
      final recommendations = scoredEvents.take(count).toList();

      print('🎉 Našiel som ${recommendations.length} odporúčaní');

      // Debug: Vypíš top 5
      for (int i = 0; i < min(5, recommendations.length); i++) {
        final r = recommendations[i];
        String mainCat = CategoryMapper.getMainCategory(r.event.category);
        double mainScore = (r.scoreBreakdown['main_category'] ?? 0) * 100;
        double subScore = (r.scoreBreakdown['sub_category'] ?? 0) * 100;
        double favBonus = (r.scoreBreakdown['favorite_bonus'] ?? 0) * 100; // 🔥 NOVÉ

        print('  ${i+1}. ${r.event.title}');
        print('      [$mainCat/${r.event.category}]');

        if (favBonus > 0) {
          print('      Skóre: ${(r.score * 100).toInt()}% (hlavná: ${mainScore.toInt()}%, pod: ${subScore.toInt()}%, bonus: ${favBonus.toInt()}% ⭐)');
        } else {
          print('      Skóre: ${(r.score * 100).toInt()}% (hlavná: ${mainScore.toInt()}%, pod: ${subScore.toInt()}%)');
        }
      }

      return recommendations;

    } catch (e, stackTrace) {
      print('❌ Chyba pri získavaní odporúčaní: $e');
      print('Stack trace: $stackTrace');
      return [];
    }
  }
}