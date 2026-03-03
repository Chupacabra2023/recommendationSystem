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

The recommendation engine (`lib/services/recommendation_engine.dart`) implements a weighted scoring system with **default weights** optimized for category matching:

- **Main Category Match** (20%): Matches events to user's preferred main categories - highest weight for broad preference matching
- **Sub-Category Match** (16%): Provides finer-grained preference matching within main categories
- **Distance** (16%): Prioritizes events closer to user location using Haversine formula
- **Rating** (16%): Considers event ratings (new events get neutral 0.5 score)
- **Popularity** (16%): Based on attendee count (normalized 0-100)
- **Favorite Bonus** (16%): Extra weight for events matching sub-categories of favorited events

**Interactive Weight Adjustment**: Users can adjust weights via the UI (tune icon in RecommendationsViewScreen). The weights are **interconnected** - when one weight increases, others decrease proportionally to maintain a 100% total. Use `RecommendationEngine.resetWeights()` to restore default weights (Main: 20%, Others: 16%).

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
- **Event**: Represents an event with category, location (GeoPoint), date, attendees, rating, `maxAttendees` (capacity limit), and `testDistanceKm` (for testing). Events display as "FULL" when `attendees.length >= maxAttendees`.
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
- `generateTestEvents(count)`: Creates test events with random categories, dates, ratings, and `maxAttendees` (4-100 participants)
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
- Default weights: Main Category 20%, all others 16% each. Users can adjust weights interactively via UI
- When adjusting weights in UI, all components remain interconnected - total always equals 100%
- New events without ratings get neutral 0.5 rating score to avoid penalization
- Empty user profiles (new users) get 0.5 main category match for all events
- Unknown subcategories to user get 5% match score (exploration factor)
- Events matching sub-categories of favorited events receive bonus based on favorite weight
- Visited events are automatically excluded from recommendations

## UI Structure

- **RecommendationTestScreen** (`lib/screens/recommendation_test_screen.dart`): Testing interface for generating test data and viewing recommendations
- **RecommendationsViewScreen** (`lib/screens/recommendations_view_screen.dart`): Displays personalized recommendations for a user
  - **Weight Adjustment Dialog**: Users can tune scoring weights interactively (tune icon)
  - **Export Results**: Exports top 5 recommendations to a text file with full breakdown (download icon)

## Export Functionality

The app includes an export feature (`_exportResults()` in RecommendationsViewScreen) that:
- Generates a formatted text file with top 5 recommended events
- Includes current weight configuration
- Shows detailed score breakdown for each event (category match, distance, rating, popularity, favorite bonus)
- Displays both percentage scores and actual values (e.g., distance in km, rating value)
- Uses `share_plus` package to allow sharing the exported file via system share dialog
- Files are saved to app's documents directory with timestamp: `recommendations_export_YYYY-MM-DD_HH-mm-ss.txt`

**Example Output**: See `example_export.txt` in the project root for a sample of the exported format.

## Firebase Configuration

The project requires `google-services.json` in `android/app/` for Firebase integration. Firebase Core is initialized at app startup before running the Flutter app.

## Notes

- The codebase uses Slovak language for UI strings and comments
- Test data is centered around Bratislava, Slovakia (coordinates: 48.1486, 17.1077)
- The recommendation algorithm uses equal weights (16.67% each) by default, but these can be adjusted by users through the UI
- Weight adjustments are interconnected - increasing one weight automatically decreases others proportionally
