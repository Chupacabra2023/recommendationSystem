"""
Content-Based Event Recommendation System - Evaluation Script
Leave-one-out evaluation across 8 weight configurations and 5 user profiles.
Uses only standard Python libraries.
"""

import sys
import math
import csv

# Force UTF-8 output on Windows so Slovak characters print correctly
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# 1. CATEGORIES
# ---------------------------------------------------------------------------

CATEGORIES = {
    "Sports": [
        "Ball sports", "Athletics", "Strength & Conditioning",
        "Winter sports", "Watercraft sports", "Extreme sports",
        "Individual sports", "Recreational sports", "Team sports",
    ],
    "Music & Entertainment": ["Koncert", "Festival", "Karaoke", "DJ Set", "Iný koncert"],
    "Art & Culture": ["Film", "Výstava", "Maľovanie / kreatívne umenie"],
    "Education": ["Jazykový kurz", "Osobný rozvoj", "Workshop (ručné práce)"],
    "Nature & Outdoor": ["Turistika", "Botanická záhrada"],
    "Community & Social": ["Speed dating", "Street meetup"],
    "Business & Tech": ["Pitch Night", "Hackathon"],
    "Food & Drinks": ["Food festival", "Street food"],
}

# Reverse map: sub_category → main_category
SUB_TO_MAIN = {sub: main for main, subs in CATEGORIES.items() for sub in subs}

# ---------------------------------------------------------------------------
# 2. SYNTHETIC EVENT DATA  (50 events)
# ---------------------------------------------------------------------------

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

# Quick look-up by id
EVENT_BY_ID = {e["id"]: e for e in EVENTS}

USERS = [
    {"id": "u01", "name": "User 1", "visited_event_ids": ["e42"], "favorite_event_ids": ["e42"], "max_distance_km": 25.0},
    {"id": "u02", "name": "User 2", "visited_event_ids": ["e12", "e88"], "favorite_event_ids": ["e88"], "max_distance_km": 25.0},
    {"id": "u03", "name": "User 3", "visited_event_ids": ["e05", "e91", "e33"], "favorite_event_ids": ["e05"], "max_distance_km": 25.0},
    {"id": "u04", "name": "User 4", "visited_event_ids": ["e21", "e44", "e09", "e76"], "favorite_event_ids": ["e21", "e76"], "max_distance_km": 25.0},
    {"id": "u05", "name": "User 5", "visited_event_ids": ["e15", "e62", "e38", "e02", "e55"], "favorite_event_ids": ["e15", "e55"], "max_distance_km": 25.0},
    {"id": "u06", "name": "User 6", "visited_event_ids": ["e01", "e19", "e82", "e47", "e93", "e28"], "favorite_event_ids": ["e01", "e82"], "max_distance_km": 25.0},
    {"id": "u07", "name": "User 7", "visited_event_ids": ["e11", "e67", "e04", "e30", "e85", "e51", "e22"], "favorite_event_ids": ["e11", "e85"], "max_distance_km": 25.0},
    {"id": "u08", "name": "User 8", "visited_event_ids": ["e08", "e59", "e14", "e97", "e23", "e41", "e66", "e03"], "favorite_event_ids": ["e08", "e97", "e03"], "max_distance_km": 25.0},
    {"id": "u09", "name": "User 9", "visited_event_ids": ["e10", "e35", "e72", "e50", "e18", "e81", "e29", "e40", "e06"], "favorite_event_ids": ["e10", "e50", "e06"], "max_distance_km": 25.0},
    {"id": "u10", "name": "User 10", "visited_event_ids": ["e13", "e99", "e46", "e25", "e80", "e07", "e37", "e61", "e54", "e17"], "favorite_event_ids": ["e13", "e80", "e17"], "max_distance_km": 25.0},
    {"id": "u11", "name": "User 11", "visited_event_ids": ["e20", "e71", "e52", "e90", "e31", "e64", "e16", "e49", "e83", "e39", "e01"], "favorite_event_ids": ["e20", "e90", "e01"], "max_distance_km": 25.0},
    {"id": "u12", "name": "User 12", "visited_event_ids": ["e24", "e60", "e84", "e45", "e95", "e32", "e77", "e14", "e58", "e02", "e68", "e21"], "favorite_event_ids": ["e24", "e95", "e21"], "max_distance_km": 25.0},
    {"id": "u13", "name": "User 13", "visited_event_ids": ["e27", "e53", "e89", "e36", "e70", "e43", "e15", "e96", "e04", "e65", "e26", "e79", "e11"], "favorite_event_ids": ["e27", "e70", "e11"], "max_distance_km": 25.0},
    {"id": "u14", "name": "User 14", "visited_event_ids": ["e09", "e81", "e34", "e63", "e18", "e92", "e48", "e05", "e75", "e29", "e57", "e12", "e87", "e38"], "favorite_event_ids": ["e09", "e92", "e38", "e57"], "max_distance_km": 25.0},
    {"id": "u15", "name": "User 15", "visited_event_ids": ["e01", "e02", "e03", "e04", "e05", "e06", "e07", "e08", "e09", "e10", "e11", "e12", "e13", "e14", "e15"], "favorite_event_ids": ["e01", "e08", "e15"], "max_distance_km": 25.0},
    {"id": "u16", "name": "User 16", "visited_event_ids": ["e16", "e17", "e18", "e19", "e20", "e21", "e22", "e23", "e24", "e25", "e26", "e27", "e28", "e29", "e30", "e31"], "favorite_event_ids": ["e16", "e24", "e31"], "max_distance_km": 25.0},
    {"id": "u17", "name": "User 17", "visited_event_ids": ["e32", "e33", "e34", "e35", "e36", "e37", "e38", "e39", "e40", "e41", "e42", "e43", "e44", "e45", "e46", "e47", "e48"], "favorite_event_ids": ["e32", "e40", "e48"], "max_distance_km": 25.0},
    {"id": "u18", "name": "User 18", "visited_event_ids": ["e49", "e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60", "e61", "e62", "e63", "e64", "e65", "e66"], "favorite_event_ids": ["e49", "e58", "e66"], "max_distance_km": 25.0},
    {"id": "u19", "name": "User 19", "visited_event_ids": ["e67", "e68", "e69", "e70", "e71", "e72", "e73", "e74", "e75", "e76", "e77", "e78", "e79", "e80", "e81", "e82", "e83", "e84", "e85"], "favorite_event_ids": ["e67", "e76", "e85"], "max_distance_km": 25.0},
    {"id": "u20", "name": "User 20", "visited_event_ids": ["e86", "e87", "e88", "e89", "e90", "e91", "e92", "e93", "e94", "e95", "e96", "e97", "e98", "e99", "e01", "e02", "e03", "e04", "e05", "e06"], "favorite_event_ids": ["e86", "e94", "e06"], "max_distance_km": 25.0},
    {"id": "u21", "name": "User 21", "visited_event_ids": ["e07", "e08", "e09", "e10", "e11", "e12", "e13", "e14", "e15", "e16", "e17", "e18", "e19", "e20", "e21", "e22", "e23", "e24", "e25", "e26", "e27"], "favorite_event_ids": ["e07", "e17", "e27"], "max_distance_km": 25.0},
    {"id": "u22", "name": "User 22", "visited_event_ids": ["e28", "e29", "e30", "e31", "e32", "e33", "e34", "e35", "e36", "e37", "e38", "e39", "e40", "e41", "e42", "e43", "e44", "e45", "e46", "e47", "e48", "e49"], "favorite_event_ids": ["e28", "e38", "e49"], "max_distance_km": 25.0},
    {"id": "u23", "name": "User 23", "visited_event_ids": ["e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60", "e61", "e62", "e63", "e64", "e65", "e66", "e67", "e68", "e69", "e70", "e71", "e72"], "favorite_event_ids": ["e50", "e61", "e72"], "max_distance_km": 25.0},
    {"id": "u24", "name": "User 24", "visited_event_ids": ["e73", "e74", "e75", "e76", "e77", "e78", "e79", "e80", "e81", "e82", "e83", "e84", "e85", "e86", "e87", "e88", "e89", "e90", "e91", "e92", "e93", "e94", "e95", "e96"], "favorite_event_ids": ["e73", "e85", "e96"], "max_distance_km": 25.0},
    {"id": "u25", "name": "User 25", "visited_event_ids": ["e97", "e98", "e99", "e01", "e02", "e03", "e04", "e05", "e06", "e07", "e08", "e09", "e10", "e11", "e12", "e13", "e14", "e15", "e16", "e17", "e18", "e19", "e20", "e21", "e22"], "favorite_event_ids": ["e97", "e09", "e22"], "max_distance_km": 25.0},
    {"id": "u26", "name": "User 26", "visited_event_ids": ["e23", "e24", "e25", "e26", "e27", "e28", "e29", "e30", "e31", "e32", "e33", "e34", "e35", "e36", "e37", "e38", "e39", "e40", "e41", "e42", "e43", "e44", "e45", "e46", "e47", "e48"], "favorite_event_ids": ["e23", "e35", "e48"], "max_distance_km": 25.0},
    {"id": "u27", "name": "User 27", "visited_event_ids": ["e49", "e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60", "e61", "e62", "e63", "e64", "e65", "e66", "e67", "e68", "e69", "e70", "e71", "e72", "e73", "e74", "e75"], "favorite_event_ids": ["e49", "e62", "e75"], "max_distance_km": 25.0},
    {"id": "u28", "name": "User 28", "visited_event_ids": ["e76", "e77", "e78", "e79", "e80", "e81", "e82", "e83", "e84", "e85", "e86", "e87", "e88", "e89", "e90", "e91", "e92", "e93", "e94", "e95", "e96", "e97", "e98", "e99", "e01", "e02", "e03", "e04"], "favorite_event_ids": ["e76", "e90", "e04"], "max_distance_km": 25.0},
    {"id": "u29", "name": "User 29", "visited_event_ids": ["e05", "e06", "e07", "e08", "e09", "e10", "e11", "e12", "e13", "e14", "e15", "e16", "e17", "e18", "e19", "e20", "e21", "e22", "e23", "e24", "e25", "e26", "e27", "e28", "e29", "e30", "e31", "e32", "e33"], "favorite_event_ids": ["e05", "e19", "e33"], "max_distance_km": 25.0},
    {"id": "u30", "name": "User 30", "visited_event_ids": ["e34", "e35", "e36", "e37", "e38", "e39", "e40", "e41", "e42", "e43", "e44", "e45", "e46", "e47", "e48", "e49", "e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60", "e61", "e62", "e63"], "favorite_event_ids": ["e34", "e48", "e63"], "max_distance_km": 25.0},
    {"id": "u31", "name": "User 31", "visited_event_ids": ["e64", "e65", "e66", "e67", "e68", "e69", "e70", "e71", "e72", "e73", "e74", "e75", "e76", "e77", "e78", "e79", "e80", "e81", "e82", "e83", "e84", "e85", "e86", "e87", "e88", "e89", "e90", "e91", "e92", "e93", "e94"], "favorite_event_ids": ["e64", "e79", "e94"], "max_distance_km": 25.0},
    {"id": "u32", "name": "User 32", "visited_event_ids": ["e95", "e96", "e97", "e98", "e99", "e01", "e02", "e03", "e04", "e05", "e06", "e07", "e08", "e09", "e10", "e11", "e12", "e13", "e14", "e15", "e16", "e17", "e18", "e19", "e20", "e21", "e22", "e23", "e24", "e25", "e26", "e27"], "favorite_event_ids": ["e95", "e11", "e27"], "max_distance_km": 25.0},
    {"id": "u33", "name": "User 33", "visited_event_ids": ["e28", "e29", "e30", "e31", "e32", "e33", "e34", "e35", "e36", "e37", "e38", "e39", "e40", "e41", "e42", "e43", "e44", "e45", "e46", "e47", "e48", "e49", "e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60"], "favorite_event_ids": ["e28", "e44", "e60"], "max_distance_km": 25.0},
    {"id": "u34", "name": "User 34", "visited_event_ids": ["e61", "e62", "e63", "e64", "e65", "e66", "e67", "e68", "e69", "e70", "e71", "e72", "e73", "e74", "e75", "e76", "e77", "e78", "e79", "e80", "e81", "e82", "e83", "e84", "e85", "e86", "e87", "e88", "e89", "e90", "e91", "e92", "e93", "e94"], "favorite_event_ids": ["e61", "e77", "e94"], "max_distance_km": 25.0},
    {"id": "u35", "name": "User 35", "visited_event_ids": ["e95", "e96", "e97", "e98", "e99", "e01", "e02", "e03", "e04", "e05", "e06", "e07", "e08", "e09", "e10", "e11", "e12", "e13", "e14", "e15", "e16", "e17", "e18", "e19", "e20", "e21", "e22", "e23", "e24", "e25", "e26", "e27", "e28", "e29", "e30"], "favorite_event_ids": ["e95", "e12", "e30"], "max_distance_km": 25.0},
    {"id": "u36", "name": "User 36", "visited_event_ids": ["e31", "e32", "e33", "e34", "e35", "e36", "e37", "e38", "e39", "e40", "e41", "e42", "e43", "e44", "e45", "e46", "e47", "e48", "e49", "e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60", "e61", "e62", "e63", "e64", "e65", "e66"], "favorite_event_ids": ["e31", "e49", "e66"], "max_distance_km": 25.0},
    {"id": "u37", "name": "User 37", "visited_event_ids": ["e67", "e68", "e69", "e70", "e71", "e72", "e73", "e74", "e75", "e76", "e77", "e78", "e79", "e80", "e81", "e82", "e83", "e84", "e85", "e86", "e87", "e88", "e89", "e90", "e91", "e92", "e93", "e94", "e95", "e96", "e97", "e98", "e99", "e01", "e02", "e03", "e04"], "favorite_event_ids": ["e67", "e83", "e04"], "max_distance_km": 25.0},
    {"id": "u38", "name": "User 38", "visited_event_ids": ["e05", "e06", "e07", "e08", "e09", "e10", "e11", "e12", "e13", "e14", "e15", "e16", "e17", "e18", "e19", "e20", "e21", "e22", "e23", "e24", "e25", "e26", "e27", "e28", "e29", "e30", "e31", "e32", "e33", "e34", "e35", "e36", "e37", "e38", "e39", "e40", "e41", "e42"], "favorite_event_ids": ["e05", "e24", "e42"], "max_distance_km": 25.0},
    {"id": "u39", "name": "User 39", "visited_event_ids": ["e43", "e44", "e45", "e46", "e47", "e48", "e49", "e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60", "e61", "e62", "e63", "e64", "e65", "e66", "e67", "e68", "e69", "e70", "e71", "e72", "e73", "e74", "e75", "e76", "e77", "e78", "e79", "e80", "e81"], "favorite_event_ids": ["e43", "e62", "e81"], "max_distance_km": 25.0},
    {"id": "u40", "name": "User 40", "visited_event_ids": ["e82", "e83", "e84", "e85", "e86", "e87", "e88", "e89", "e90", "e91", "e92", "e93", "e94", "e95", "e96", "e97", "e98", "e99", "e01", "e02", "e03", "e04", "e05", "e06", "e07", "e08", "e09", "e10", "e11", "e12", "e13", "e14", "e15", "e16", "e17", "e18", "e19", "e20", "e21", "e22"], "favorite_event_ids": ["e82", "e01", "e22"], "max_distance_km": 25.0},
    {"id": "u41", "name": "User 41", "visited_event_ids": ["e23", "e24", "e25", "e26", "e27", "e28", "e29", "e30", "e31", "e32", "e33", "e34", "e35", "e36", "e37", "e38", "e39", "e40", "e41", "e42", "e43", "e44", "e45", "e46", "e47", "e48", "e49", "e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60", "e61", "e62", "e63"], "favorite_event_ids": ["e23", "e43", "e63"], "max_distance_km": 25.0},
    {"id": "u42", "name": "User 42", "visited_event_ids": ["e64", "e65", "e66", "e67", "e68", "e69", "e70", "e71", "e72", "e73", "e74", "e75", "e76", "e77", "e78", "e79", "e80", "e81", "e82", "e83", "e84", "e85", "e86", "e87", "e88", "e89", "e90", "e91", "e92", "e93", "e94", "e95", "e96", "e97", "e98", "e99", "e01", "e02", "e03", "e04", "e05", "e06"], "favorite_event_ids": ["e64", "e85", "e06"], "max_distance_km": 25.0},
    {"id": "u43", "name": "User 43", "visited_event_ids": ["e07", "e08", "e09", "e10", "e11", "e12", "e13", "e14", "e15", "e16", "e17", "e18", "e19", "e20", "e21", "e22", "e23", "e24", "e25", "e26", "e27", "e28", "e29", "e30", "e31", "e32", "e33", "e34", "e35", "e36", "e37", "e38", "e39", "e40", "e41", "e42", "e43", "e44", "e45", "e46", "e47", "e48", "e49"], "favorite_event_ids": ["e07", "e28", "e49"], "max_distance_km": 25.0},
    {"id": "u44", "name": "User 44", "visited_event_ids": ["e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60", "e61", "e62", "e63", "e64", "e65", "e66", "e67", "e68", "e69", "e70", "e71", "e72", "e73", "e74", "e75", "e76", "e77", "e78", "e79", "e80", "e81", "e82", "e83", "e84", "e85", "e86", "e87", "e88", "e89", "e90", "e91", "e92", "e93"], "favorite_event_ids": ["e50", "e71", "e93"], "max_distance_km": 25.0},
    {"id": "u45", "name": "User 45", "visited_event_ids": ["e94", "e95", "e96", "e97", "e98", "e99", "e01", "e02", "e03", "e04", "e05", "e06", "e07", "e08", "e09", "e10", "e11", "e12", "e13", "e14", "e15", "e16", "e17", "e18", "e19", "e20", "e21", "e22", "e23", "e24", "e25", "e26", "e27", "e28", "e29", "e30", "e31", "e32", "e33", "e34", "e35", "e36", "e37", "e38", "e39"], "favorite_event_ids": ["e94", "e15", "e39"], "max_distance_km": 25.0},
    {"id": "u46", "name": "User 46", "visited_event_ids": ["e40", "e41", "e42", "e43", "e44", "e45", "e46", "e47", "e48", "e49", "e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60", "e61", "e62", "e63", "e64", "e65", "e66", "e67", "e68", "e69", "e70", "e71", "e72", "e73", "e74", "e75", "e76", "e77", "e78", "e79", "e80", "e81", "e82", "e83", "e84", "e85"], "favorite_event_ids": ["e40", "e63", "e85"], "max_distance_km": 25.0},
    {"id": "u47", "name": "User 47", "visited_event_ids": ["e86", "e87", "e88", "e89", "e90", "e91", "e92", "e93", "e94", "e95", "e96", "e97", "e98", "e99", "e01", "e02", "e03", "e04", "e05", "e06", "e07", "e08", "e09", "e10", "e11", "e12", "e13", "e14", "e15", "e16", "e17", "e18", "e19", "e20", "e21", "e22", "e23", "e24", "e25", "e26", "e27", "e28", "e29", "e30", "e31", "e32", "e33"], "favorite_event_ids": ["e86", "e09", "e33"], "max_distance_km": 25.0},
    {"id": "u48", "name": "User 48", "visited_event_ids": ["e34", "e35", "e36", "e37", "e38", "e39", "e40", "e41", "e42", "e43", "e44", "e45", "e46", "e47", "e48", "e49", "e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60", "e61", "e62", "e63", "e64", "e65", "e66", "e67", "e68", "e69", "e70", "e71", "e72", "e73", "e74", "e75", "e76", "e77", "e78", "e79", "e80"], "favorite_event_ids": ["e34", "e57", "e80"], "max_distance_km": 25.0},
    {"id": "u49", "name": "User 49", "visited_event_ids": ["e81", "e82", "e83", "e84", "e85", "e86", "e87", "e88", "e89", "e90", "e91", "e92", "e93", "e94", "e95", "e96", "e97", "e98", "e99", "e01", "e02", "e03", "e04", "e05", "e06", "e07", "e08", "e09", "e10", "e11", "e12", "e13", "e14", "e15", "e16", "e17", "e18", "e19", "e20", "e21", "e22", "e23", "e24", "e25", "e26", "e27", "e28", "e29"], "favorite_event_ids": ["e81", "e05", "e29"], "max_distance_km": 25.0},
    {"id": "u50", "name": "User 50", "visited_event_ids": ["e30", "e31", "e32", "e33", "e34", "e35", "e36", "e37", "e38", "e39", "e40", "e41", "e42", "e43", "e44", "e45", "e46", "e47", "e48", "e49", "e50", "e51", "e52", "e53", "e54", "e55", "e56", "e57", "e58", "e59", "e60", "e61", "e62", "e63", "e64", "e65", "e66", "e67", "e68", "e69", "e70", "e71", "e72", "e73", "e74", "e75", "e76", "e77", "e78", "e79"], "favorite_event_ids": ["e30", "e54", "e79"], "max_distance_km": 25.0},
]


WEIGHT_CONFIGS = {
   
    "T01":        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00),  # 100% main
    "T02":        (0.00, 1.00, 0.00, 0.00, 0.00, 0.00),  # 100% sub
    "T03":        (0.00, 0.00, 0.00, 0.00, 0.00, 1.00),  # 100% fav
    "T04":        (0.60, 0.30, 0.00, 0.00, 0.00, 0.10),  # main dominant
    "T05":        (0.50, 0.40, 0.00, 0.00, 0.00, 0.10),  # main+sub
    "T06":        (0.40, 0.40, 0.00, 0.00, 0.00, 0.20),  # viac fav
    "T07":        (0.50, 0.30, 0.00, 0.00, 0.00, 0.20),  # main+fav
    "T08":        (0.70, 0.20, 0.00, 0.00, 0.00, 0.10),  # veľmi main
    "T09":        (0.33, 0.33, 0.00, 0.00, 0.00, 0.34),  # rovnomerne
    "T10":        (0.60, 0.20, 0.00, 0.00, 0.00, 0.20),  # main+fav silné
    "T11":        (0.40, 0.50, 0.00, 0.00, 0.00, 0.10),  # sub dominant
    "T12":        (0.30, 0.60, 0.00, 0.00, 0.00, 0.10),  # sub veľmi dominant
    "T13":        (0.20, 0.60, 0.00, 0.00, 0.00, 0.20),  # sub+fav
    "T14":        (0.50, 0.20, 0.00, 0.00, 0.00, 0.30),  # main+fav silné
    "T15":        (0.30, 0.30, 0.00, 0.00, 0.00, 0.40),  # fav dominant
    "T16":        (0.45, 0.45, 0.00, 0.00, 0.00, 0.10),  # main=sub
    "T17":        (0.55, 0.35, 0.00, 0.00, 0.00, 0.10),  # mierne main
    "T18":        (0.35, 0.55, 0.00, 0.00, 0.00, 0.10),  # mierne sub
    "T19":        (0.40, 0.30, 0.00, 0.00, 0.00, 0.30),  # vyvážené s fav
    "T20":        (0.25, 0.25, 0.00, 0.00, 0.00, 0.50),  # fav veľmi dominant
    
}





# ---------------------------------------------------------------------------
# 5. SCORING ENGINE
# ---------------------------------------------------------------------------

def build_user_profile(user, exclude_event_id=None):
    """
    Compute preference ratios from visited events.
    Returns (main_counts, sub_counts, total_visits, fav_subcategories).
    If exclude_event_id is given, that event is treated as hidden (LOO).
    """
    visited = [
        eid for eid in user["visited_event_ids"]
        if eid != exclude_event_id
    ]
    total = len(visited)

    main_counts = {}
    sub_counts = {}
    for eid in visited:
        ev = EVENT_BY_ID[eid]
        main_counts[ev["main_category"]] = main_counts.get(ev["main_category"], 0) + 1
        sub_counts[ev["sub_category"]]   = sub_counts.get(ev["sub_category"],   0) + 1

    # Determine favourite subcategories (based on all favourites, not affected by LOO)
    fav_subs = set()
    for eid in user["favorite_event_ids"]:
        fav_subs.add(EVENT_BY_ID[eid]["sub_category"])

    return main_counts, sub_counts, total, fav_subs


def score_event(event, main_counts, sub_counts, total_visits, fav_subs, weights):
    """
    Compute the weighted recommendation score for a single event.
    weights = (w_main, w_sub, w_dist, w_rating, w_pop, w_fav)
    """
    w_main, w_sub, w_dist, w_rating, w_pop, w_fav = weights

    # --- C_main ---
    if total_visits == 0:
        c_main = 0.5
    else:
        c_main = main_counts.get(event["main_category"], 0) / total_visits
        if c_main == 0:
            c_main = 0.05  # exploration factor for never-seen main category

    # --- C_sub ---
    if total_visits == 0:
        c_sub = 0.5
    else:
        c_sub = sub_counts.get(event["sub_category"], 0) / total_visits
        # 0.0 is valid – no exploration boost for subcategory per spec

    # --- D (distance) ---
    d_score = 1.0 / (1.0 + event["distance_km"] / 10.0)

    # --- R (rating) ---
    r_score = event["rating"] / 5.0

    # --- P (popularity) ---
    p_score = min(event["attendees"] / event["max_attendees"], 1.0)

    # --- B_fav ---
    b_fav = 1.0 if event["sub_category"] in fav_subs else 0.0

    total = (
        w_main   * c_main  +
        w_sub    * c_sub   +
        w_dist   * d_score +
        w_rating * r_score +
        w_pop    * p_score +
        w_fav    * b_fav
    )

    return total


def get_recommendations(user, weights, exclude_event_id=None, top_k=5):
    """
    Return the top-k recommended event IDs for a user,
    excluding already-visited events (and optionally one hidden event).
    """
    main_counts, sub_counts, total_visits, fav_subs = build_user_profile(
        user, exclude_event_id=exclude_event_id
    )

    visited_set = set(user["visited_event_ids"])
    # In LOO the hidden event is also excluded from candidates
    if exclude_event_id:
        visited_set.add(exclude_event_id)

    scored = []
    for ev in EVENTS:
        if ev["id"] in visited_set:
            continue
        s = score_event(ev, main_counts, sub_counts, total_visits, fav_subs, weights)
        scored.append((s, ev["id"]))

    scored.sort(key=lambda x: -x[0])
    return [eid for _, eid in scored[:top_k]]

# ---------------------------------------------------------------------------
# 6. LEAVE-ONE-OUT EVALUATION
# ---------------------------------------------------------------------------

def precision_at_k(user, weights, top_k=5):
    """
    Leave-one-out Precision@K.
    For each visited event: hide it, check if TOP-K contains at least one event
    from the same MAIN category as the hidden event → 1 hit, else 0.
    Precision = hits / total_visited
    """
    hits = 0
    visited = user["visited_event_ids"]
    for hidden_id in visited:
        hidden_main = EVENT_BY_ID[hidden_id]["main_category"]
        recs = get_recommendations(user, weights, exclude_event_id=hidden_id, top_k=top_k)
        # Hit if any recommended event belongs to the same main category
        for rec_id in recs:
            if EVENT_BY_ID[rec_id]["main_category"] == hidden_main:
                hits += 1
                break

    return hits / len(visited) if visited else 0.0

# ---------------------------------------------------------------------------
# 7. RUN EVALUATION & PRINT RESULTS TABLE
# ---------------------------------------------------------------------------

def fmt_pct(value):
    return f"{round(value * 100):3d}%"


def run_evaluation():
    """
    Runs LOO evaluation, prints the results table and per-user breakdown,
    and returns evaluation_results dict for export:

        {
          user_id: {
            "name": str,
            "visited": int,
            "configs": { config_name: (hits, total), ... }
          }, ...
        }
    """
    col_width = 10

    # --- Pre-compute hits for every (user, config) pair (single LOO pass) ---
    # Structure: hits_table[user_id][cfg_name] = (hits, n)
    hits_table = {u["id"]: {} for u in USERS}

    for cfg_name, weights in WEIGHT_CONFIGS.items():
        for user in USERS:
            hits = 0
            n = len(user["visited_event_ids"])
            for hidden_id in user["visited_event_ids"]:
                hidden_main = EVENT_BY_ID[hidden_id]["main_category"]
                recs = get_recommendations(user, weights, exclude_event_id=hidden_id, top_k=5)
                if any(EVENT_BY_ID[r]["main_category"] == hidden_main for r in recs):
                    hits += 1
            hits_table[user["id"]][cfg_name] = (hits, n)

    # --- Summary table ---
    user_names = [u["name"] for u in USERS]
    header    = f"{'Config':<14}" + "".join(f" | {name:<{col_width}}" for name in user_names) + f" | {'AVG':>{col_width}}"
    separator = "-" * len(header)

    print("\n" + "=" * len(header))
    print("  EVALUATION RESULTS  -  Leave-One-Out  Precision@5")
    print("=" * len(header))
    print(header)
    print(separator)

    best_config = None
    best_avg    = -1.0

    for cfg_name in WEIGHT_CONFIGS:
        user_scores = []
        for user in USERS:
            hits, n = hits_table[user["id"]][cfg_name]
            user_scores.append(hits / n if n else 0.0)

        avg = sum(user_scores) / len(user_scores)
        if avg > best_avg:
            best_avg    = avg
            best_config = cfg_name

        row = (
            f"{cfg_name:<14}" +
            "".join(f" | {fmt_pct(s):>{col_width}}" for s in user_scores) +
            f" | {fmt_pct(avg):>{col_width}}"
        )
        print(row)

    print(separator)
    print(f"\nBest configuration: '{best_config}'  (AVG Precision@5 = {fmt_pct(best_avg)})\n")

    # --- Per-user breakdown ---
    print("=" * len(header))
    print("  PER-USER DETAILS  (visited events -> hits)")
    print("=" * len(header))

    for user in USERS:
        print(f"\n  {user['name']}  (visited: {len(user['visited_event_ids'])} events)")
        for cfg_name in WEIGHT_CONFIGS:
            hits, n = hits_table[user["id"]][cfg_name]
            p = hits / n if n else 0.0
            print(f"    {cfg_name:<14}  {hits:2d}/{n}  ({fmt_pct(p)})")

    print()

    # --- Build and return evaluation_results for export ---
    evaluation_results = {}
    for user in USERS:
        evaluation_results[user["id"]] = {
            "name":    user["name"],
            "visited": len(user["visited_event_ids"]),
            "configs": hits_table[user["id"]],   # {cfg_name: (hits, n)}
        }
    return evaluation_results


def compute_avg_per_config(evaluation_results):
    """
    Returns {config_name: avg_precision} across all users.
    AVG = mean of per-user precision (hits/n).
    """
    avgs = {}
    for cfg_name in WEIGHT_CONFIGS:
        precisions = []
        for data in evaluation_results.values():
            hits, n = data["configs"][cfg_name]
            precisions.append(hits / n if n > 0 else 0.0)
        avgs[cfg_name] = sum(precisions) / len(precisions)
    return avgs


def print_avg_summary(avgs):
    """Print a compact Config | AVG table and highlight the best config."""
    best_cfg = max(avgs, key=avgs.get)
    print("\n" + "=" * 35)
    print("  AVG Precision@5  (vsetky useri)")
    print("=" * 35)
    print(f"  {'Config':<14} | {'AVG':>6}")
    print("  " + "-" * 25)
    for cfg_name, avg in avgs.items():
        marker = " <-- BEST" if cfg_name == best_cfg else ""
        print(f"  {cfg_name:<14} | {fmt_pct(avg):>6}{marker}")
    print("=" * 35)
    print(f"\n  Najlepsia konfig: '{best_cfg}'  ({fmt_pct(avgs[best_cfg])})\n")


def export_avg_table(avgs, filename="avg_summary.csv"):
    """Save Config | AVG to a small CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Config", "AVG_Precision@5"])
        for cfg_name, avg in avgs.items():
            writer.writerow([cfg_name, f"{round(avg * 100, 1)}%"])
    print(f"AVG prehlad ulozeny ako {filename}")


def export_summary_table(evaluation_results, filename="evaluation_summary.csv"):
    rows = []
    for user_id, data in evaluation_results.items():
        row = {
            "user":           data["name"],
            "visited_events": data["visited"],
        }
        for config_name, (correct, total) in data["configs"].items():
            percent = round((correct / total) * 100, 1) if total > 0 else 0
            row[config_name] = f"{correct}/{total} ({percent}%)"
        rows.append(row)

    fieldnames = list(rows[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Detailny prehlad ulozeny ako {filename}")


if __name__ == "__main__":
    assert len(EVENTS) == 150, f"Expected 150 events, got {len(EVENTS)}"
    assert len(USERS)  ==  50, f"Expected 50 users,  got {len(USERS)}"
    print(f"Loaded {len(EVENTS)} events and {len(USERS)} users.")

    evaluation_results = run_evaluation()

    avgs = compute_avg_per_config(evaluation_results)
    print_avg_summary(avgs)
    export_avg_table(avgs)
    export_summary_table(evaluation_results)