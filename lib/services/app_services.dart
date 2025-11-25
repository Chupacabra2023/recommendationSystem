import 'recommendation_service.dart';
import 'recommendation_engine.dart';

class AppServices {
  // Singleton pattern
  static final AppServices _instance = AppServices._internal();
  factory AppServices() => _instance;
  AppServices._internal();

  // ════════════════════════════════════════════════════════
  // Recommendation Service
  // ════════════════════════════════════════════════════════

  RecommendationService? _recommendationService;

  RecommendationService get recommendationService {
    _recommendationService ??= _createRecommendationService();
    return _recommendationService!;
  }

  RecommendationService _createRecommendationService() {
    // Tu môžeš prepínať medzi implementáciami:

    // FÁZA 1: Client-side (teraz) ✅
    return RecommendationEngine();

    // FÁZA 2: Server-side (neskôr)
    // return ServerSideRecommendationService();

    // FÁZA 3: Hybrid (budúcnosť)
    // return HybridRecommendationService(...);
  }

  // Reset pre testovanie
  void reset() {
    _recommendationService = null;
  }
}