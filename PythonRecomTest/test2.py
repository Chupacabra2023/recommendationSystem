import sys
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

CATEGORIES = {
    "Sports": ["Ball sports", "Athletics", "Strength & Conditioning", "Winter sports", "Watercraft sports", "Extreme sports", "Individual sports", "Recreational sports", "Team sports"],
    "Music & Entertainment": ["Koncert", "Festival", "Karaoke", "DJ Set", "Iný koncert"],
    "Art & Culture": ["Film", "Výstava", "Maľovanie / kreatívne umenie"],
    "Education": ["Jazykový kurz", "Osobný rozvoj", "Workshop (ručné práce)"],
    "Nature & Outdoor": ["Turistika", "Botanická záhrada"],
    "Community & Social": ["Speed dating", "Street meetup"],
    "Business & Tech": ["Pitch Night", "Hackathon"],
    "Food & Drinks": ["Food festival", "Street food"],
}

EVENTS = [
    # --- Sports (14 events) ---
    {"id": "e01", "title": "Mestský futbalový turnaj",    "main_category": "Sports", "sub_category": "Ball sports",              "rating": 4.2, "total_ratings": 15, "distance_km":  2.1, "attendees": 22, "max_attendees": 30},
    {"id": "e02", "title": "Basketbal open-air",          "main_category": "Sports", "sub_category": "Ball sports",              "rating": 3.8, "total_ratings":  8, "distance_km":  5.4, "attendees": 14, "max_attendees": 20},
    {"id": "e03", "title": "Bežecký maratón",             "main_category": "Sports", "sub_category": "Athletics",                "rating": 4.6, "total_ratings": 20, "distance_km":  8.0, "attendees": 80, "max_attendees": 100},
    {"id": "e04", "title": "Dráhová atletika",            "main_category": "Sports", "sub_category": "Athletics",                "rating": 3.5, "total_ratings":  5, "distance_km": 12.0, "attendees": 30, "max_attendees": 60},
    {"id": "e05", "title": "CrossFit challenge",          "main_category": "Sports", "sub_category": "Strength & Conditioning",  "rating": 4.1, "total_ratings": 11, "distance_km":  3.3, "attendees": 18, "max_attendees": 25},
    {"id": "e06", "title": "Zimný lyžiarsky kurz",        "main_category": "Sports", "sub_category": "Winter sports",            "rating": 4.8, "total_ratings": 18, "distance_km": 22.0, "attendees": 35, "max_attendees": 40},
    {"id": "e07", "title": "Paddleboard závod",           "main_category": "Sports", "sub_category": "Watercraft sports",        "rating": 4.0, "total_ratings":  9, "distance_km": 16.0, "attendees": 12, "max_attendees": 20},
    {"id": "e08", "title": "Skalolezecký tréning",        "main_category": "Sports", "sub_category": "Extreme sports",           "rating": 4.3, "total_ratings": 13, "distance_km":  7.5, "attendees": 10, "max_attendees": 15},
    {"id": "e09", "title": "Tenis open",                  "main_category": "Sports", "sub_category": "Individual sports",        "rating": 3.9, "total_ratings":  7, "distance_km":  4.2, "attendees": 16, "max_attendees": 32},
    {"id": "e10", "title": "Plávanie – hobby liga",       "main_category": "Sports", "sub_category": "Recreational sports",      "rating": 3.6, "total_ratings":  6, "distance_km":  1.5, "attendees": 20, "max_attendees": 50},
    {"id": "e11", "title": "Volejbalový turnaj",          "main_category": "Sports", "sub_category": "Team sports",              "rating": 4.4, "total_ratings": 16, "distance_km":  9.0, "attendees": 24, "max_attendees": 30},
    {"id": "e12", "title": "Futsal weekend",              "main_category": "Sports", "sub_category": "Ball sports",              "rating": 4.0, "total_ratings": 10, "distance_km":  6.8, "attendees": 20, "max_attendees": 24},
    {"id": "e13", "title": "Fitness boot camp",           "main_category": "Sports", "sub_category": "Strength & Conditioning",  "rating": 3.7, "total_ratings":  4, "distance_km": 11.0, "attendees": 15, "max_attendees": 20},
    {"id": "e14", "title": "Horská cyklistika",           "main_category": "Sports", "sub_category": "Extreme sports",           "rating": 4.5, "total_ratings": 14, "distance_km": 18.0, "attendees":  8, "max_attendees": 12},

    # --- Music & Entertainment (8 events) ---
    {"id": "e15", "title": "Rock koncert v klube",        "main_category": "Music & Entertainment", "sub_category": "Koncert",    "rating": 4.7, "total_ratings": 19, "distance_km":  1.8, "attendees": 90, "max_attendees": 100},
    {"id": "e16", "title": "Letný hudobný festival",      "main_category": "Music & Entertainment", "sub_category": "Festival",   "rating": 4.9, "total_ratings": 20, "distance_km": 24.0, "attendees": 95, "max_attendees": 100},
    {"id": "e17", "title": "Karaoke noc",                 "main_category": "Music & Entertainment", "sub_category": "Karaoke",    "rating": 3.4, "total_ratings":  3, "distance_km":  2.5, "attendees": 28, "max_attendees": 40},
    {"id": "e18", "title": "DJ Set v bare",               "main_category": "Music & Entertainment", "sub_category": "DJ Set",     "rating": 4.0, "total_ratings": 12, "distance_km":  3.0, "attendees": 55, "max_attendees": 80},
    {"id": "e19", "title": "Jazzový večer",               "main_category": "Music & Entertainment", "sub_category": "Iný koncert","rating": 4.3, "total_ratings": 11, "distance_km":  5.2, "attendees": 40, "max_attendees": 60},
    {"id": "e20", "title": "Klasická hudba – Filharmónia","main_category": "Music & Entertainment", "sub_category": "Koncert",    "rating": 4.6, "total_ratings": 17, "distance_km":  0.8, "attendees": 70, "max_attendees": 80},
    {"id": "e21", "title": "Indie folk festival",         "main_category": "Music & Entertainment", "sub_category": "Festival",   "rating": 4.2, "total_ratings":  9, "distance_km": 20.0, "attendees": 60, "max_attendees": 75},
    {"id": "e22", "title": "Pop Karaoke bar",             "main_category": "Music & Entertainment", "sub_category": "Karaoke",    "rating": 3.2, "total_ratings":  2, "distance_km":  4.5, "attendees": 18, "max_attendees": 35},

    # --- Art & Culture (6 events) ---
    {"id": "e23", "title": "Filmový festival",            "main_category": "Art & Culture", "sub_category": "Film",                         "rating": 4.5, "total_ratings": 16, "distance_km":  6.0, "attendees": 50, "max_attendees": 60},
    {"id": "e24", "title": "Moderné umenie – výstava",    "main_category": "Art & Culture", "sub_category": "Výstava",                      "rating": 4.1, "total_ratings": 10, "distance_km":  1.2, "attendees": 30, "max_attendees": 50},
    {"id": "e25", "title": "Maľovanie portrétu",          "main_category": "Art & Culture", "sub_category": "Maľovanie / kreatívne umenie", "rating": 3.8, "total_ratings":  6, "distance_km":  3.7, "attendees": 12, "max_attendees": 16},
    {"id": "e26", "title": "Fotografická výstava",        "main_category": "Art & Culture", "sub_category": "Výstava",                      "rating": 4.3, "total_ratings": 13, "distance_km":  2.0, "attendees": 25, "max_attendees": 40},
    {"id": "e27", "title": "Krátke filmy – projekcia",   "main_category": "Art & Culture", "sub_category": "Film",                         "rating": 4.0, "total_ratings":  8, "distance_km":  7.8, "attendees": 35, "max_attendees": 50},
    {"id": "e28", "title": "Akvarel workshop",            "main_category": "Art & Culture", "sub_category": "Maľovanie / kreatívne umenie", "rating": 4.2, "total_ratings": 11, "distance_km":  5.5, "attendees": 10, "max_attendees": 14},

    # --- Education (5 events) ---
    {"id": "e29", "title": "Anglický jazyk – začiatočníci","main_category": "Education", "sub_category": "Jazykový kurz",          "rating": 4.0, "total_ratings": 14, "distance_km":  2.3, "attendees": 20, "max_attendees": 25},
    {"id": "e30", "title": "Španielčina online",          "main_category": "Education", "sub_category": "Jazykový kurz",          "rating": 3.9, "total_ratings":  7, "distance_km":  0.5, "attendees": 15, "max_attendees": 30},
    {"id": "e31", "title": "Mindfulness & koučing",       "main_category": "Education", "sub_category": "Osobný rozvoj",          "rating": 4.4, "total_ratings": 15, "distance_km":  4.9, "attendees": 22, "max_attendees": 30},
    {"id": "e32", "title": "Workshop – origami",          "main_category": "Education", "sub_category": "Workshop (ručné práce)", "rating": 3.7, "total_ratings":  5, "distance_km":  8.6, "attendees":  8, "max_attendees": 12},
    {"id": "e33", "title": "Keramika pre začiatočníkov",  "main_category": "Education", "sub_category": "Workshop (ručné práce)", "rating": 4.1, "total_ratings": 10, "distance_km":  6.1, "attendees": 10, "max_attendees": 14},

    # --- Nature & Outdoor (4 events) ---
    {"id": "e34", "title": "Turistika – Malé Karpaty",    "main_category": "Nature & Outdoor", "sub_category": "Turistika",           "rating": 4.6, "total_ratings": 18, "distance_km": 14.0, "attendees": 18, "max_attendees": 25},
    {"id": "e35", "title": "Nočný výstup na vrch",        "main_category": "Nature & Outdoor", "sub_category": "Turistika",           "rating": 4.8, "total_ratings": 12, "distance_km": 20.0, "attendees": 14, "max_attendees": 20},
    {"id": "e36", "title": "Botanická záhrada – jar",     "main_category": "Nature & Outdoor", "sub_category": "Botanická záhrada",   "rating": 4.0, "total_ratings":  9, "distance_km":  3.5, "attendees": 30, "max_attendees": 60},
    {"id": "e37", "title": "Záhrada – fotovychádzka",     "main_category": "Nature & Outdoor", "sub_category": "Botanická záhrada",   "rating": 3.8, "total_ratings":  4, "distance_km":  4.0, "attendees": 20, "max_attendees": 40},

    # --- Community & Social (4 events) ---
    {"id": "e38", "title": "Speed dating večer",          "main_category": "Community & Social", "sub_category": "Speed dating",  "rating": 3.5, "total_ratings":  6, "distance_km":  1.0, "attendees": 20, "max_attendees": 30},
    {"id": "e39", "title": "Speed dating 30+",            "main_category": "Community & Social", "sub_category": "Speed dating",  "rating": 3.8, "total_ratings":  8, "distance_km":  2.2, "attendees": 16, "max_attendees": 24},
    {"id": "e40", "title": "Street meetup – Staré Mesto", "main_category": "Community & Social", "sub_category": "Street meetup", "rating": 4.1, "total_ratings": 11, "distance_km":  0.9, "attendees": 35, "max_attendees": 50},
    {"id": "e41", "title": "Susedská párty",              "main_category": "Community & Social", "sub_category": "Street meetup", "rating": 3.9, "total_ratings":  7, "distance_km":  1.5, "attendees": 25, "max_attendees": 40},

    # --- Business & Tech (4 events) ---
    {"id": "e42", "title": "Startup Pitch Night",         "main_category": "Business & Tech", "sub_category": "Pitch Night",  "rating": 4.2, "total_ratings": 14, "distance_km":  3.6, "attendees": 40, "max_attendees": 60},
    {"id": "e43", "title": "Investičný pitch",            "main_category": "Business & Tech", "sub_category": "Pitch Night",  "rating": 4.5, "total_ratings": 17, "distance_km":  5.0, "attendees": 35, "max_attendees": 50},
    {"id": "e44", "title": "AI Hackathon 2025",           "main_category": "Business & Tech", "sub_category": "Hackathon",    "rating": 4.7, "total_ratings": 20, "distance_km":  8.0, "attendees": 55, "max_attendees": 60},
    {"id": "e45", "title": "Web dev hackathon",           "main_category": "Business & Tech", "sub_category": "Hackathon",    "rating": 4.3, "total_ratings": 12, "distance_km": 10.0, "attendees": 45, "max_attendees": 60},

    # --- Food & Drinks (5 events) ---
    {"id": "e46", "title": "Street food trh",             "main_category": "Food & Drinks", "sub_category": "Street food",   "rating": 4.3, "total_ratings": 16, "distance_km":  1.3, "attendees": 70, "max_attendees": 100},
    {"id": "e47", "title": "Azijský food festival",       "main_category": "Food & Drinks", "sub_category": "Food festival", "rating": 4.5, "total_ratings": 18, "distance_km":  7.2, "attendees": 85, "max_attendees": 100},
    {"id": "e48", "title": "Lokálne jedlo – market",      "main_category": "Food & Drinks", "sub_category": "Food festival", "rating": 4.0, "total_ratings":  9, "distance_km":  2.8, "attendees": 60, "max_attendees": 80},
    {"id": "e49", "title": "Uličný food trh – zima",      "main_category": "Food & Drinks", "sub_category": "Street food",   "rating": 3.9, "total_ratings":  7, "distance_km":  3.2, "attendees": 45, "max_attendees": 70},
    {"id": "e50", "title": "Pivný festival",              "main_category": "Food & Drinks", "sub_category": "Food festival", "rating": 4.6, "total_ratings": 20, "distance_km": 15.0, "attendees": 90, "max_attendees": 100},

# --- Sports (e51–e57) ---
    {"id": "e51", "title": "Plážový volejbal",             "main_category": "Sports", "sub_category": "Team sports",             "rating": 4.1, "total_ratings": 10, "distance_km":  5.0, "attendees": 18, "max_attendees": 24},
    {"id": "e52", "title": "Ranný beh v parku",            "main_category": "Sports", "sub_category": "Athletics",               "rating": 3.9, "total_ratings":  6, "distance_km":  1.2, "attendees": 25, "max_attendees": 50},
    {"id": "e53", "title": "Kickbox tréning",              "main_category": "Sports", "sub_category": "Extreme sports",          "rating": 4.2, "total_ratings": 12, "distance_km":  3.8, "attendees":  9, "max_attendees": 15},
    {"id": "e54", "title": "Bedminton liga",               "main_category": "Sports", "sub_category": "Individual sports",       "rating": 3.7, "total_ratings":  5, "distance_km":  6.5, "attendees": 14, "max_attendees": 20},
    {"id": "e55", "title": "Aqua aerobik",                 "main_category": "Sports", "sub_category": "Recreational sports",     "rating": 3.8, "total_ratings":  7, "distance_km":  2.9, "attendees": 20, "max_attendees": 30},
    {"id": "e56", "title": "Snowboard camp",               "main_category": "Sports", "sub_category": "Winter sports",           "rating": 4.7, "total_ratings": 15, "distance_km": 21.0, "attendees": 20, "max_attendees": 25},
    {"id": "e57", "title": "Joga v parku",                 "main_category": "Sports", "sub_category": "Strength & Conditioning", "rating": 4.0, "total_ratings":  9, "distance_km":  1.8, "attendees": 22, "max_attendees": 35},

    # --- Music & Entertainment (e58–e63) ---
    {"id": "e58", "title": "Drum & Bass večer",            "main_category": "Music & Entertainment", "sub_category": "DJ Set",      "rating": 4.1, "total_ratings":  8, "distance_km":  2.1, "attendees": 60, "max_attendees": 80},
    {"id": "e59", "title": "Akustický koncert v kaviarni", "main_category": "Music & Entertainment", "sub_category": "Koncert",     "rating": 4.4, "total_ratings": 13, "distance_km":  0.9, "attendees": 35, "max_attendees": 45},
    {"id": "e60", "title": "Metalový festival",            "main_category": "Music & Entertainment", "sub_category": "Festival",    "rating": 4.3, "total_ratings": 16, "distance_km": 18.0, "attendees": 80, "max_attendees": 100},
    {"id": "e61", "title": "Retro karaoke noc",            "main_category": "Music & Entertainment", "sub_category": "Karaoke",     "rating": 3.6, "total_ratings":  4, "distance_km":  3.3, "attendees": 22, "max_attendees": 40},
    {"id": "e62", "title": "Funk & Soul párty",            "main_category": "Music & Entertainment", "sub_category": "Iný koncert", "rating": 4.2, "total_ratings": 11, "distance_km":  4.7, "attendees": 45, "max_attendees": 60},
    {"id": "e63", "title": "Elektronická hudba – open air","main_category": "Music & Entertainment", "sub_category": "Festival",    "rating": 4.6, "total_ratings": 19, "distance_km": 12.0, "attendees": 90, "max_attendees": 100},

    # --- Art & Culture (e64–e69) ---
    {"id": "e64", "title": "Divadelná improvizácia",       "main_category": "Art & Culture", "sub_category": "Film",                         "rating": 4.0, "total_ratings":  8, "distance_km":  2.5, "attendees": 40, "max_attendees": 60},
    {"id": "e65", "title": "Socha a keramika – výstava",   "main_category": "Art & Culture", "sub_category": "Výstava",                      "rating": 4.2, "total_ratings": 12, "distance_km":  1.5, "attendees": 28, "max_attendees": 45},
    {"id": "e66", "title": "Graffiti workshop",            "main_category": "Art & Culture", "sub_category": "Maľovanie / kreatívne umenie", "rating": 3.9, "total_ratings":  7, "distance_km":  5.2, "attendees": 10, "max_attendees": 16},
    {"id": "e67", "title": "Dokumentárny film večer",      "main_category": "Art & Culture", "sub_category": "Film",                         "rating": 4.1, "total_ratings":  9, "distance_km":  3.0, "attendees": 30, "max_attendees": 50},
    {"id": "e68", "title": "Výstava modernej fotografie",  "main_category": "Art & Culture", "sub_category": "Výstava",                      "rating": 4.4, "total_ratings": 14, "distance_km":  2.3, "attendees": 22, "max_attendees": 40},
    {"id": "e69", "title": "Ilustrácia pre začiatočníkov", "main_category": "Art & Culture", "sub_category": "Maľovanie / kreatívne umenie", "rating": 3.8, "total_ratings":  5, "distance_km":  6.8, "attendees":  8, "max_attendees": 14},

    # --- Education (e70–e75) ---
    {"id": "e70", "title": "Nemčina – konverzácia",        "main_category": "Education", "sub_category": "Jazykový kurz",          "rating": 4.1, "total_ratings": 11, "distance_km":  3.1, "attendees": 18, "max_attendees": 25},
    {"id": "e71", "title": "Verejné vystupovanie",         "main_category": "Education", "sub_category": "Osobný rozvoj",          "rating": 4.3, "total_ratings": 13, "distance_km":  4.5, "attendees": 20, "max_attendees": 30},
    {"id": "e72", "title": "Tvorivé písanie",              "main_category": "Education", "sub_category": "Workshop (ručné práce)", "rating": 3.9, "total_ratings":  6, "distance_km":  7.2, "attendees":  9, "max_attendees": 12},
    {"id": "e73", "title": "Francúzština pre mierne pokr.","main_category": "Education", "sub_category": "Jazykový kurz",          "rating": 4.0, "total_ratings":  8, "distance_km":  1.9, "attendees": 16, "max_attendees": 20},
    {"id": "e74", "title": "Meditácia a stres manažment",  "main_category": "Education", "sub_category": "Osobný rozvoj",          "rating": 4.5, "total_ratings": 16, "distance_km":  2.7, "attendees": 25, "max_attendees": 30},
    {"id": "e75", "title": "Drôtená bižutéria – workshop", "main_category": "Education", "sub_category": "Workshop (ručné práce)", "rating": 3.6, "total_ratings":  4, "distance_km":  9.3, "attendees":  7, "max_attendees": 10},

    # --- Nature & Outdoor (e76–e81) ---
    {"id": "e76", "title": "Cyklovýlet – Záhorie",         "main_category": "Nature & Outdoor", "sub_category": "Turistika",         "rating": 4.4, "total_ratings": 15, "distance_km": 16.0, "attendees": 20, "max_attendees": 30},
    {"id": "e77", "title": "Ranný výstup – Devín",         "main_category": "Nature & Outdoor", "sub_category": "Turistika",         "rating": 4.7, "total_ratings": 18, "distance_km": 11.0, "attendees": 16, "max_attendees": 20},
    {"id": "e78", "title": "Jesenná záhrada – prehliadka", "main_category": "Nature & Outdoor", "sub_category": "Botanická záhrada", "rating": 3.9, "total_ratings":  7, "distance_km":  3.8, "attendees": 25, "max_attendees": 50},
    {"id": "e79", "title": "Nočná príroda – pozorovanie",  "main_category": "Nature & Outdoor", "sub_category": "Turistika",         "rating": 4.5, "total_ratings": 11, "distance_km": 19.0, "attendees": 12, "max_attendees": 18},
    {"id": "e80", "title": "Exotická záhrada – tour",      "main_category": "Nature & Outdoor", "sub_category": "Botanická záhrada", "rating": 4.1, "total_ratings":  9, "distance_km":  4.5, "attendees": 35, "max_attendees": 60},
    {"id": "e81", "title": "Nordic walking – Rusovce",     "main_category": "Nature & Outdoor", "sub_category": "Turistika",         "rating": 3.8, "total_ratings":  5, "distance_km":  8.5, "attendees": 14, "max_attendees": 25},

    # --- Community & Social (e82–e87) ---
    {"id": "e82", "title": "Speed dating – mladí",         "main_category": "Community & Social", "sub_category": "Speed dating",  "rating": 3.7, "total_ratings":  6, "distance_km":  1.3, "attendees": 18, "max_attendees": 28},
    {"id": "e83", "title": "Komunitný piknik",             "main_category": "Community & Social", "sub_category": "Street meetup", "rating": 4.2, "total_ratings": 12, "distance_km":  2.0, "attendees": 40, "max_attendees": 60},
    {"id": "e84", "title": "Speed dating – 40+",           "main_category": "Community & Social", "sub_category": "Speed dating",  "rating": 3.9, "total_ratings":  8, "distance_km":  3.1, "attendees": 14, "max_attendees": 22},
    {"id": "e85", "title": "Susedský swap – výmena vecí",  "main_category": "Community & Social", "sub_category": "Street meetup", "rating": 4.0, "total_ratings":  9, "distance_km":  0.7, "attendees": 30, "max_attendees": 50},
    {"id": "e86", "title": "Jazykový tandem meetup",       "main_category": "Community & Social", "sub_category": "Street meetup", "rating": 4.3, "total_ratings": 14, "distance_km":  1.8, "attendees": 22, "max_attendees": 35},
    {"id": "e87", "title": "Speed dating – mix kultúr",    "main_category": "Community & Social", "sub_category": "Speed dating",  "rating": 4.1, "total_ratings": 10, "distance_km":  2.6, "attendees": 20, "max_attendees": 30},

    # --- Business & Tech (e88–e93) ---
    {"id": "e88", "title": "Fintech pitch evening",        "main_category": "Business & Tech", "sub_category": "Pitch Night", "rating": 4.3, "total_ratings": 15, "distance_km":  4.2, "attendees": 38, "max_attendees": 55},
    {"id": "e89", "title": "Green tech hackathon",         "main_category": "Business & Tech", "sub_category": "Hackathon",   "rating": 4.6, "total_ratings": 18, "distance_km":  9.0, "attendees": 50, "max_attendees": 60},
    {"id": "e90", "title": "Healthcare startup pitch",     "main_category": "Business & Tech", "sub_category": "Pitch Night", "rating": 4.1, "total_ratings": 11, "distance_km":  6.3, "attendees": 30, "max_attendees": 50},
    {"id": "e91", "title": "Blockchain hackathon",         "main_category": "Business & Tech", "sub_category": "Hackathon",   "rating": 4.4, "total_ratings": 14, "distance_km":  7.5, "attendees": 48, "max_attendees": 60},
    {"id": "e92", "title": "EdTech pitch night",           "main_category": "Business & Tech", "sub_category": "Pitch Night", "rating": 4.0, "total_ratings":  9, "distance_km":  3.0, "attendees": 28, "max_attendees": 45},
    {"id": "e93", "title": "Cybersecurity hackathon",      "main_category": "Business & Tech", "sub_category": "Hackathon",   "rating": 4.8, "total_ratings": 20, "distance_km": 11.0, "attendees": 58, "max_attendees": 60},

    # --- Food & Drinks (e94–e100) ---
    {"id": "e94",  "title": "Vegánsky food festival",      "main_category": "Food & Drinks", "sub_category": "Food festival", "rating": 4.3, "total_ratings": 14, "distance_km":  5.5, "attendees": 75, "max_attendees": 100},
    {"id": "e95",  "title": "Burgerový street food trh",   "main_category": "Food & Drinks", "sub_category": "Street food",   "rating": 4.1, "total_ratings": 11, "distance_km":  2.1, "attendees": 55, "max_attendees": 80},
    {"id": "e96",  "title": "Syrový festival",             "main_category": "Food & Drinks", "sub_category": "Food festival", "rating": 4.4, "total_ratings": 16, "distance_km":  8.3, "attendees": 80, "max_attendees": 100},
    {"id": "e97",  "title": "Ramenový street food",        "main_category": "Food & Drinks", "sub_category": "Street food",   "rating": 4.2, "total_ratings": 12, "distance_km":  1.6, "attendees": 40, "max_attendees": 60},
    {"id": "e98",  "title": "Čokoládový festival",         "main_category": "Food & Drinks", "sub_category": "Food festival", "rating": 4.6, "total_ratings": 19, "distance_km": 10.0, "attendees": 88, "max_attendees": 100},
    {"id": "e99",  "title": "Street food – leto",          "main_category": "Food & Drinks", "sub_category": "Street food",   "rating": 4.0, "total_ratings":  8, "distance_km":  3.7, "attendees": 50, "max_attendees": 70},
    {"id": "e100", "title": "Medzinárodný food festival",  "main_category": "Food & Drinks", "sub_category": "Food festival", "rating": 4.7, "total_ratings": 20, "distance_km": 13.0, "attendees": 92, "max_attendees": 100},

    # --- EXTRA EVENTS (e101–e150) ---
    {"id": "e101", "title": "Stolnotenisový turnaj",            "main_category": "Sports", "sub_category": "Individual sports",       "rating": 4.1, "total_ratings":  9, "distance_km":  3.4, "attendees": 18, "max_attendees": 32},
    {"id": "e102", "title": "Futbalová liga – amatéri",         "main_category": "Sports", "sub_category": "Ball sports",             "rating": 3.9, "total_ratings": 12, "distance_km":  6.2, "attendees": 22, "max_attendees": 30},
    {"id": "e103", "title": "Atletika – šprinty",               "main_category": "Sports", "sub_category": "Athletics",               "rating": 4.0, "total_ratings":  7, "distance_km": 10.5, "attendees": 28, "max_attendees": 60},
    {"id": "e104", "title": "Silový tréning pre začiatočníkov", "main_category": "Sports", "sub_category": "Strength & Conditioning", "rating": 4.4, "total_ratings": 14, "distance_km":  2.2, "attendees": 20, "max_attendees": 25},
    {"id": "e105", "title": "Inline korčuľovanie meetup",       "main_category": "Sports", "sub_category": "Recreational sports",     "rating": 3.7, "total_ratings":  6, "distance_km":  1.9, "attendees": 35, "max_attendees": 60},
    {"id": "e106", "title": "Lezecká stena – tréning",          "main_category": "Sports", "sub_category": "Extreme sports",          "rating": 4.3, "total_ratings": 11, "distance_km":  7.1, "attendees": 12, "max_attendees": 18},
    {"id": "e107", "title": "Volejbal – mix tímy",              "main_category": "Sports", "sub_category": "Team sports",             "rating": 4.2, "total_ratings": 10, "distance_km":  8.3, "attendees": 24, "max_attendees": 30},
    {"id": "e108", "title": "Kajak – tréning na jazere",        "main_category": "Sports", "sub_category": "Watercraft sports",       "rating": 3.8, "total_ratings":  5, "distance_km": 15.4, "attendees": 10, "max_attendees": 20},

    {"id": "e109", "title": "Indie koncert v podniku",          "main_category": "Music & Entertainment", "sub_category": "Koncert",     "rating": 4.5, "total_ratings": 16, "distance_km":  1.1, "attendees": 40, "max_attendees": 55},
    {"id": "e110", "title": "Techno DJ night",                  "main_category": "Music & Entertainment", "sub_category": "DJ Set",      "rating": 4.1, "total_ratings":  9, "distance_km":  2.6, "attendees": 65, "max_attendees": 90},
    {"id": "e111", "title": "Open mic – karaoke show",          "main_category": "Music & Entertainment", "sub_category": "Karaoke",     "rating": 3.5, "total_ratings":  6, "distance_km":  3.9, "attendees": 25, "max_attendees": 40},
    {"id": "e112", "title": "Jazz & wine večer",                "main_category": "Music & Entertainment", "sub_category": "Iný koncert", "rating": 4.4, "total_ratings": 12, "distance_km":  5.8, "attendees": 38, "max_attendees": 60},
    {"id": "e113", "title": "Mini hudobný festival – park",     "main_category": "Music & Entertainment", "sub_category": "Festival",    "rating": 4.2, "total_ratings": 10, "distance_km": 12.4, "attendees": 75, "max_attendees": 100},
    {"id": "e114", "title": "Akustický set – kaviareň",         "main_category": "Music & Entertainment", "sub_category": "Koncert",     "rating": 4.0, "total_ratings":  8, "distance_km":  0.7, "attendees": 30, "max_attendees": 45},

    {"id": "e115", "title": "Galéria – výstava súčasného umenia","main_category": "Art & Culture", "sub_category": "Výstava",                      "rating": 4.2, "total_ratings": 13, "distance_km":  1.6, "attendees": 26, "max_attendees": 50},
    {"id": "e116", "title": "Filmový klub – európsky film",     "main_category": "Art & Culture", "sub_category": "Film",                         "rating": 4.1, "total_ratings":  9, "distance_km":  4.9, "attendees": 40, "max_attendees": 70},
    {"id": "e117", "title": "Kreslenie – portrét workshop",     "main_category": "Art & Culture", "sub_category": "Maľovanie / kreatívne umenie", "rating": 3.9, "total_ratings":  7, "distance_km":  3.2, "attendees": 14, "max_attendees": 18},
    {"id": "e118", "title": "Fotografia – street výstava",      "main_category": "Art & Culture", "sub_category": "Výstava",                      "rating": 4.4, "total_ratings": 15, "distance_km":  2.1, "attendees": 22, "max_attendees": 45},
    {"id": "e119", "title": "Krátke filmy – večerná projekcia", "main_category": "Art & Culture", "sub_category": "Film",                         "rating": 4.0, "total_ratings":  8, "distance_km":  7.0, "attendees": 33, "max_attendees": 55},
    {"id": "e120", "title": "Akvarel – pokročilí",              "main_category": "Art & Culture", "sub_category": "Maľovanie / kreatívne umenie", "rating": 4.3, "total_ratings": 11, "distance_km":  5.9, "attendees": 10, "max_attendees": 14},

    {"id": "e121", "title": "Nemčina – začiatočníci",           "main_category": "Education", "sub_category": "Jazykový kurz",          "rating": 4.0, "total_ratings": 10, "distance_km":  2.8, "attendees": 18, "max_attendees": 25},
    {"id": "e122", "title": "Taliančina – konverzácia",         "main_category": "Education", "sub_category": "Jazykový kurz",          "rating": 3.8, "total_ratings":  6, "distance_km":  1.4, "attendees": 16, "max_attendees": 20},
    {"id": "e123", "title": "Workshop – drevorezba",            "main_category": "Education", "sub_category": "Workshop (ručné práce)", "rating": 4.2, "total_ratings": 12, "distance_km":  8.1, "attendees":  9, "max_attendees": 12},
    {"id": "e124", "title": "Osobný rozvoj – time management",  "main_category": "Education", "sub_category": "Osobný rozvoj",          "rating": 4.5, "total_ratings": 15, "distance_km":  3.6, "attendees": 22, "max_attendees": 30},
    {"id": "e125", "title": "Workshop – šitie pre začiatočníkov","main_category": "Education", "sub_category": "Workshop (ručné práce)", "rating": 3.7, "total_ratings":  5, "distance_km":  6.9, "attendees":  8, "max_attendees": 14},
    {"id": "e126", "title": "Meditácia – večerný kurz",         "main_category": "Education", "sub_category": "Osobný rozvoj",          "rating": 4.1, "total_ratings":  9, "distance_km":  2.5, "attendees": 24, "max_attendees": 35},

    {"id": "e127", "title": "Turistika – hrad Devín",           "main_category": "Nature & Outdoor", "sub_category": "Turistika",         "rating": 4.6, "total_ratings": 17, "distance_km": 11.8, "attendees": 18, "max_attendees": 25},
    {"id": "e128", "title": "Botanická záhrada – prehliadka",    "main_category": "Nature & Outdoor", "sub_category": "Botanická záhrada", "rating": 4.0, "total_ratings":  8, "distance_km":  3.3, "attendees": 28, "max_attendees": 60},
    {"id": "e129", "title": "Nočný výlet – lesný chodník",      "main_category": "Nature & Outdoor", "sub_category": "Turistika",         "rating": 4.4, "total_ratings": 11, "distance_km": 18.6, "attendees": 12, "max_attendees": 18},
    {"id": "e130", "title": "Záhrada – fotowalk",               "main_category": "Nature & Outdoor", "sub_category": "Botanická záhrada", "rating": 3.9, "total_ratings":  7, "distance_km":  4.7, "attendees": 20, "max_attendees": 40},

    {"id": "e131", "title": "Street meetup – Ružinov",          "main_category": "Community & Social", "sub_category": "Street meetup", "rating": 4.1, "total_ratings": 10, "distance_km":  1.2, "attendees": 34, "max_attendees": 50},
    {"id": "e132", "title": "Speed dating – študenti",          "main_category": "Community & Social", "sub_category": "Speed dating",  "rating": 3.6, "total_ratings":  7, "distance_km":  2.0, "attendees": 18, "max_attendees": 28},
    {"id": "e133", "title": "Komunitná grilovačka",             "main_category": "Community & Social", "sub_category": "Street meetup", "rating": 4.3, "total_ratings": 14, "distance_km":  2.7, "attendees": 42, "max_attendees": 60},
    {"id": "e134", "title": "Speed dating – 30 až 45",          "main_category": "Community & Social", "sub_category": "Speed dating",  "rating": 3.9, "total_ratings":  9, "distance_km":  3.4, "attendees": 16, "max_attendees": 24},
    {"id": "e135", "title": "Susedské hry – park",              "main_category": "Community & Social", "sub_category": "Street meetup", "rating": 4.0, "total_ratings":  8, "distance_km":  0.8, "attendees": 30, "max_attendees": 45},

    {"id": "e136", "title": "Startup networking brunch",        "main_category": "Business & Tech", "sub_category": "Pitch Night", "rating": 4.2, "total_ratings": 12, "distance_km":  3.1, "attendees": 36, "max_attendees": 60},
    {"id": "e137", "title": "Pitch Night – FinTech edition",    "main_category": "Business & Tech", "sub_category": "Pitch Night", "rating": 4.4, "total_ratings": 16, "distance_km":  5.7, "attendees": 40, "max_attendees": 65},
    {"id": "e138", "title": "Hackathon – smart city",           "main_category": "Business & Tech", "sub_category": "Hackathon",   "rating": 4.6, "total_ratings": 18, "distance_km":  9.8, "attendees": 52, "max_attendees": 60},
    {"id": "e139", "title": "Hackathon – web security",         "main_category": "Business & Tech", "sub_category": "Hackathon",   "rating": 4.7, "total_ratings": 20, "distance_km": 12.2, "attendees": 58, "max_attendees": 60},
    {"id": "e140", "title": "AI meetup – praktické demo",       "main_category": "Business & Tech", "sub_category": "Pitch Night", "rating": 4.1, "total_ratings":  9, "distance_km":  4.4, "attendees": 28, "max_attendees": 50},

    {"id": "e141", "title": "Street food – večerný trh",        "main_category": "Food & Drinks", "sub_category": "Street food",   "rating": 4.2, "total_ratings": 13, "distance_km":  1.7, "attendees": 55, "max_attendees": 80},
    {"id": "e142", "title": "Food festival – lokálne chute",    "main_category": "Food & Drinks", "sub_category": "Food festival", "rating": 4.5, "total_ratings": 18, "distance_km":  7.9, "attendees": 78, "max_attendees": 100},
    {"id": "e143", "title": "Street food – vegan corner",      "main_category": "Food & Drinks", "sub_category": "Street food",   "rating": 4.0, "total_ratings":  9, "distance_km":  2.4, "attendees": 42, "max_attendees": 60},
    {"id": "e144", "title": "Čokoláda & dezerty festival",      "main_category": "Food & Drinks", "sub_category": "Food festival", "rating": 4.6, "total_ratings": 20, "distance_km":  9.6, "attendees": 88, "max_attendees": 100},
    {"id": "e145", "title": "Gastro market – zimná edícia",     "main_category": "Food & Drinks", "sub_category": "Food festival", "rating": 4.1, "total_ratings": 11, "distance_km": 12.8, "attendees": 70, "max_attendees": 95},
    {"id": "e146", "title": "Zimný tréning – lyže & kondícia",  "main_category": "Sports", "sub_category": "Winter sports",           "rating": 4.7, "total_ratings": 15, "distance_km": 21.5, "attendees": 22, "max_attendees": 30},
    {"id": "e147", "title": "Beh – intervaly na dráhe",         "main_category": "Sports", "sub_category": "Athletics",               "rating": 4.0, "total_ratings":  8, "distance_km":  2.6, "attendees": 25, "max_attendees": 50},
    {"id": "e148", "title": "Joga & mobilita – ráno",           "main_category": "Sports", "sub_category": "Strength & Conditioning", "rating": 4.2, "total_ratings": 12, "distance_km":  1.0, "attendees": 30, "max_attendees": 40},
    {"id": "e149", "title": "Metal night – klubový koncert",    "main_category": "Music & Entertainment", "sub_category": "Koncert",     "rating": 4.3, "total_ratings": 14, "distance_km":  2.9, "attendees": 55, "max_attendees": 80},
    {"id": "e150", "title": "Workshop – keramika (pokročilí)",  "main_category": "Education", "sub_category": "Workshop (ručné práce)", "rating": 4.4, "total_ratings": 16, "distance_km":  6.4, "attendees": 10, "max_attendees": 14},

]

EVENT_BY_ID = {e["id"]: e for e in EVENTS}

USERS = [
    {
        "id": "u1", "name": "Sporťák",
        "visited_event_ids": ["e01", "e02", "e03", "e04", "e05", "e06", "e23", "e46"],
        "expected_category": "Sports"
    },
    {
        "id": "u2", "name": "Hudobník",
        "visited_event_ids": ["e15", "e16", "e18", "e19", "e20", "e03"],
        "expected_category": "Music & Entertainment"
    },
    {
        "id": "u3", "name": "Umelec",
        "visited_event_ids": ["e23", "e24", "e26", "e28", "e15"],
        "expected_category": "Art & Culture"
    },
    {
        "id": "u4", "name": "Technik",
        "visited_event_ids": ["e42", "e43", "e44", "e31"],
        "expected_category": "Business & Tech"
    },
    {
        "id": "u5", "name": "Foodie",
        "visited_event_ids": ["e46", "e47", "e48", "e50", "e40"],
        "expected_category": "Food & Drinks"
    },
]

WEIGHT_CONFIGS = {
    "W01 (main=100%)": (1.00, 0.00),
    "W02 (main=90%)":  (0.90, 0.10),
    "W03 (main=80%)":  (0.80, 0.20),
    "W04 (main=70%)":  (0.70, 0.30),
    "W05 (main=60%)":  (0.60, 0.40),
    "W06 (main=50%)":  (0.50, 0.50),
    "W07 (main=40%)":  (0.40, 0.60),
    "W08 (main=30%)":  (0.30, 0.70),
    "W09 (main=20%)":  (0.20, 0.80),
    "W10 (sub=100%)":  (0.00, 1.00),
}

def build_profile(user):
    total = len(user["visited_event_ids"])
    main_counts, sub_counts = {}, {}
    for eid in user["visited_event_ids"]:
        ev = EVENT_BY_ID[eid]
        main_counts[ev["main_category"]] = main_counts.get(ev["main_category"], 0) + 1
        sub_counts[ev["sub_category"]]   = sub_counts.get(ev["sub_category"],   0) + 1
    return main_counts, sub_counts, total

def score_event(ev, main_counts, sub_counts, total, w_main, w_sub):
    c_main = main_counts.get(ev["main_category"], 0.05) / total if total else 0.5
    c_sub  = sub_counts.get(ev["sub_category"],   0.00) / total if total else 0.5
    return w_main * c_main + w_sub * c_sub

def get_top5(user, w_main, w_sub):
    main_counts, sub_counts, total = build_profile(user)
    visited = set(user["visited_event_ids"])
    scored = [
        (score_event(ev, main_counts, sub_counts, total, w_main, w_sub), ev)
        for ev in EVENTS if ev["id"] not in visited
    ]
    scored.sort(key=lambda x: -x[0])
    return scored[:5]

# --- VÝPIS ---
for cfg_name, (w_main, w_sub) in WEIGHT_CONFIGS.items():
    all_pass = True
    results = []
    for user in USERS:
        top5 = get_top5(user, w_main, w_sub)
        cats = [ev["main_category"] for _, ev in top5]
        hit = user["expected_category"] in cats
        if not hit:
            all_pass = False
        results.append((user, top5, hit))

    status = "✓ VŠETCI PREŠLI" if all_pass else "✗ NIEKTORÍ NEPREŠLI"
    print(f"\n{'='*60}")
    print(f"  {cfg_name}  →  {status}")
    print(f"{'='*60}")

    for user, top5, hit in results:
        print(f"\n  {user['name']} ({'✓ PASS' if hit else '✗ FAIL'})")
        for score, ev in top5:
            marker = " ←" if ev["main_category"] == user["expected_category"] else ""
            print(f"    [{ev['main_category']:25}] {ev['title']} ({score:.3f}){marker}")