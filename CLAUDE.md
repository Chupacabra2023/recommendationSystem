# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flutter-based event recommendation system that uses Firebase Firestore as the backend. The app generates personalized event recommendations based on user preferences, location proximity, event ratings, and popularity.

## Commands

### Development
```bash
# Install dependencies
flutter pub get

# Run the app (development)
flutter run

# Run tests
flutter test

# Build for Android (debug)
flutter build apk --debug

# Build for Android (release)
flutter build apk --release

# Clean build artifacts
flutter clean
```

### Linting
```bash
# Analyze code
flutter analyze
```

## Architecture

### Core Recommendation Algorithm

The recommendation engine (`lib/services/recommendation_engine.dart`) implements a weighted scoring system:

- **Main Category Match** (30%): Matches events to user's preferred main categories
- **Sub-Category Match** (30%): Provides finer-grained preference matching within main categories
- **Distance** (20%): Prioritizes events closer to user location using Haversine formula
- **Rating** (5%): Considers event ratings (new events get neutral 0.5 score)
- **Popularity** (5%): Based on attendee count (normalized 0-100)
- **Favorite Bonus** (10%): Extra weight for events matching sub-categories of favorited events

**Note**: Scoring weights are configurable at runtime via static properties in `RecommendationEngine`. Use `RecommendationEngine.resetWeights()` to restore defaults.

### Category System

The app uses a two-tier category system defined in `lib/utils/category_mapper.dart`:
- **9 Main Categories**: Sports, Music & Entertainment, Art & Culture, Food & Drinks, Business & Tech, Education, Nature & Outdoor, Family & Kids, Community & Social
- **Sub-categories**: Each main category has multiple specific subcategories (e.g., "Ball sports" → "Sports")

The `CategoryMapper` class handles mapping between subcategories and main categories, which is critical for the recommendation algorithm.

### User Profile Generation

User preferences are calculated from visit history in `getUserProfile()`:
1. Aggregates visited events (NOT favorites - they only provide a bonus)
2. Maps subcategories to main categories
3. Calculates preference percentages for both main and subcategories
4. Returns weighted preference map

New users without visit history receive an empty profile, causing all events to be scored equally (neutral scoring).

**Important**: The `favoriteEventIds` field in `UserProfile` is NOT used to calculate preferences. It only provides a 10% bonus to events matching the same sub-categories as favorited events. This allows users to signal interest without it dominating their preference profile.

### Data Models

Located in `lib/models/recommendation_models.dart`:
- **Event**: Represents an event with category, location (GeoPoint), date, attendees, rating, and `testDistanceKm` (for testing)
- **UserProfile**: User data including location, max distance preference, `visitedEventIds` (used for preferences), and `favoriteEventIds` (used for bonus scoring)
- **ScoredEvent**: Wrapper containing an event, its recommendation score, and detailed score breakdown by component

### Service Architecture

The system uses an abstract `RecommendationService` interface (`lib/services/recommendation_service.dart`) with two methods:
- `getRecommendations()`: Returns scored and ranked events
- `getUserProfile()`: Computes user preference profile

This allows easy switching between client-side and potential server-side implementations.

### Firebase Integration

Firebase is initialized in `main.dart` before app launch. The app uses:
- **Firestore Collections**:
  - `users`: User profiles with location and visit history
  - `events`: Event data with categories, dates, locations, ratings

### Test Data Generation

`lib/services/test_data_generator.dart` provides utilities for creating test data:
- `generateTestUsers(count)`: Creates test users centered around Bratislava coordinates
- `generateTestEvents(count)`: Creates test events with random categories, dates, and ratings
- `clearTestData()`: Removes all test users and events (prefixed with "test_")

## Key Implementation Details

### Distance Calculation
Uses Haversine formula to calculate great-circle distance between two GeoPoints. Distance score is normalized using `1 / (1 + distance/10)` so closer events score higher.

### Event Filtering
Events are excluded from recommendations if:
- User has already attended (`visitedEventIds` contains event ID)
- Event date is in the past
- Event is beyond user's `maxDistanceKm` preference

### Scoring Details
- Main and sub-category matches now have equal weight (30% each) for balanced category matching
- New events without ratings get neutral 0.5 rating score to avoid penalization
- Empty user profiles (new users) get 0.5 main category match for all events
- Unknown subcategories to user get 5% match score (exploration factor)
- Events matching sub-categories of favorited events receive a 10% bonus
- Visited events are automatically excluded from recommendations

## UI Structure

- **RecommendationTestScreen** (`lib/screens/recommendation_test_screen.dart`): Testing interface for generating test data and viewing recommendations
- **RecommendationsViewScreen** (`lib/screens/recommendations_view_screen.dart`): Displays personalized recommendations for a user

## Firebase Configuration

The project requires `google-services.json` in `android/app/` for Firebase integration. Firebase Core is initialized at app startup before running the Flutter app.

## Notes

- The codebase uses Slovak language for UI strings and comments
- Test data is centered around Bratislava, Slovakia (coordinates: 48.1486, 17.1077)
- The recommendation algorithm emphasizes category matching (50% total weight across main + sub) over other factors
