import 'package:cloud_firestore/cloud_firestore.dart';

class Event {
  final String id;
  final String title;
  final String category;
  final GeoPoint location;
  final DateTime date;
  final List<String> attendees;
  final double rating;
  final int totalRatings;
  final double testDistanceKm; // 🔥 používané pri testoch
  final int maxAttendees; // 🔥 Maximálny počet účastníkov

  Event({
    required this.id,
    required this.title,
    required this.category,
    required this.location,
    required this.date,
    required this.attendees,
    this.rating = 0.0,
    this.totalRatings = 0,
    this.testDistanceKm = 0.0,
    this.maxAttendees = 100, // Default: 100 účastníkov
  });

  factory Event.fromJson(Map<String, dynamic> json, String id) {
    return Event(
      id: id,
      title: json['title'] ?? '',
      category: json['category'] ?? '',
      location: json['location'] ?? GeoPoint(0, 0),
      date: (json['date'] as Timestamp).toDate(),
      attendees: List<String>.from(json['attendees'] ?? []),
      rating: (json['rating'] ?? 0.0).toDouble(),
      totalRatings: json['totalRatings'] ?? 0,
      testDistanceKm: (json['testDistanceKm'] ?? 0).toDouble(), // 🔥 doplnené
      maxAttendees: json['maxAttendees'] ?? 100, // 🔥 doplnené
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'category': category,
      'location': location,
      'date': Timestamp.fromDate(date),
      'attendees': attendees,
      'rating': rating,
      'totalRatings': totalRatings,
      'testDistanceKm': testDistanceKm, // 🔥 uložiť do Firestore
      'maxAttendees': maxAttendees, // 🔥 uložiť do Firestore
    };
  }
}

class UserProfile {
  final String id;
  final String name;
  final GeoPoint location;
  final double maxDistanceKm;
  final List<String> visitedEventIds;
  final List<String> favoriteEventIds; // 🔥 NOVÉ: Obľúbené eventy

  UserProfile({
    required this.id,
    required this.name,
    required this.location,
    required this.maxDistanceKm,
    required this.visitedEventIds,
    this.favoriteEventIds = const [], // Defaultne prázdny zoznam
  });

  factory UserProfile.fromJson(Map<String, dynamic> json, String id) {
    return UserProfile(
      id: id,
      name: json['name'] ?? '',
      location: json['location'] ?? GeoPoint(0, 0),
      maxDistanceKm: (json['maxDistanceKm'] ?? 50).toDouble(),
      visitedEventIds: List<String>.from(json['visitedEventIds'] ?? []),
      favoriteEventIds: List<String>.from(json['favoriteEventIds'] ?? []), // 🔥 NOVÉ
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'location': location,
      'maxDistanceKm': maxDistanceKm,
      'visitedEventIds': visitedEventIds,
      'favoriteEventIds': favoriteEventIds, // 🔥 NOVÉ
    };
  }
}


class ScoredEvent {
  final Event event;
  final double score;
  final Map<String, double> scoreBreakdown;

  ScoredEvent({
    required this.event,
    required this.score,
    required this.scoreBreakdown,
  });
}
