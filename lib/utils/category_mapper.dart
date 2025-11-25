class CategoryMapper {
  // Mapa: podkategória → hlavná kategória
  static const Map<String, String> _subToMainCategory = {
    // Sports
    "Ball sports": "Sports",
    "Athletics": "Sports",
    "Combat sports": "Sports",
    "Aquatic sports": "Sports",
    "Gymnastics": "Sports",
    "Cycling sports": "Sports",
    "Winter sports": "Sports",
    "Strength & Conditioning": "Sports",
    "Outdoor sports": "Sports",
    "Motor sports": "Sports",
    "E-sports (competitive gaming)": "Sports",
    "Racquet sports": "Sports",
    "Watercraft sports": "Sports",
    "Animal sports": "Sports",
    "Extreme sports": "Sports",
    "Team sports": "Sports",
    "Individual sports": "Sports",
    "Fitness & Wellness": "Sports",
    "Precision sports": "Sports",
    "Recreational sports": "Sports",

    // Music & Entertainment
    "Koncert": "Music & Entertainment",
    "Festival": "Music & Entertainment",
    "Party / Clubbing": "Music & Entertainment",
    "Karaoke": "Music & Entertainment",
    "DJ Set": "Music & Entertainment",
    "Iný koncert": "Music & Entertainment",

    // Art & Culture
    "Film": "Art & Culture",
    "Divadlo": "Art & Culture",
    "Výstava": "Art & Culture",
    "Múzeum": "Art & Culture",
    "Literatúra / čítanie": "Art & Culture",
    "Maľovanie / kreatívne umenie": "Art & Culture",
    "Verejné zhromaždenie": "Art & Culture",
    "Protest": "Art & Culture",

    // Food & Drinks
    "Food festival": "Food & Drinks",
    "Street food": "Food & Drinks",
    "Degustácia vín": "Food & Drinks",
    "Degustácia piva": "Food & Drinks",
    "Reštauračné eventy": "Food & Drinks",
    "Grilovačka": "Food & Drinks",
    "Opekačka": "Food & Drinks",

    // Business & Tech
    "Startup meetup": "Business & Tech",
    "Networking event": "Business & Tech",
    "Konferencia": "Business & Tech",
    "Prednáška": "Business & Tech",
    "Pitch Night": "Business & Tech",
    "Veľtrh práce": "Business & Tech",
    "Workshop (IT)": "Business & Tech",
    "Hackathon": "Business & Tech",
    "Gaming turnaj": "Business & Tech",
    "E-sports": "Business & Tech",
    "Odborné prednášky": "Business & Tech",

    // Education
    "Vzdelávací kurz": "Education",
    "Workshop (ručné práce)": "Education",
    "Jazykový kurz": "Education",
    "Osobný rozvoj": "Education",
    "Tvorivé dielne": "Education",

    // Nature & Outdoor
    "Turistika": "Nature & Outdoor",
    "Výlet": "Nature & Outdoor",
    "Kempovanie": "Nature & Outdoor",
    "Návšteva parku": "Nature & Outdoor",
    "Botanická záhrada": "Nature & Outdoor",

    // Family & Kids
    "Rodinná akcia": "Family & Kids",
    "Tvorivé dielne pre deti": "Family & Kids",
    "Detské divadlo": "Family & Kids",

    // Community & Social
    "Speed dating": "Community & Social",
    "Komunitné akcie": "Community & Social",
    "Street meetup": "Community & Social",
  };

  /// Získaj hlavnú kategóriu z podkategórie
  static String getMainCategory(String subCategory) {
    return _subToMainCategory[subCategory] ?? subCategory;
  }

  /// Získaj všetky hlavné kategórie
  static List<String> get mainCategories => [
    "Sports",
    "Music & Entertainment",
    "Art & Culture",
    "Food & Drinks",
    "Business & Tech",
    "Education",
    "Nature & Outdoor",
    "Family & Kids",
    "Community & Social",
  ];

  /// Skontroluj či je to hlavná kategória
  static bool isMainCategory(String category) {
    return mainCategories.contains(category);
  }
}