import '/models/recommendation_models.dart';


/// Abstraktné rozhranie pre recommendation service
/// Umožňuje jednoducho prepínať medzi client-side / server-side / hybrid
abstract class RecommendationService {
  /// Získaj personalizované odporúčania pre užívateľa
  Future<List<ScoredEvent>> getRecommendations({
    required String userId,
    int count = 10,
    int maxDistanceKm = 50,
  });

  /// Vypočítaj užívateľský profil (preferencie kategórií)
  Future<Map<String, double>> getUserProfile(String userId);
}