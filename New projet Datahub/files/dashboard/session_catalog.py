"""
session_catalog.py — F1 Data Hub · Catalogue complet 2020–2025
═══════════════════════════════════════════════════════════════
~131 courses · 6 saisons · tous les circuits disponibles.

Source des session_key OpenF1 : https://openf1.org/#sessions
FastF1 fonctionne par nom de circuit + année (pas de session_key).
"""

# ── Correspondance circuit → coordonnées GPS ──────────────────
CIRCUIT_COORDS = {
    "Sakhir":         (26.0325,   50.5106),
    "Jeddah":         (21.6319,   39.1044),
    "Melbourne":      (-37.8497,  144.968),
    "Imola":          (44.3439,   11.7167),
    "Miami":          (25.9581,  -80.2389),
    "Monaco":         (43.7347,    7.4205),
    "Montreal":       (45.5000,  -73.5228),
    "Silverstone":    (52.0786,   -1.0169),
    "Spielberg":      (47.2197,   14.7647),
    "Budapest":       (47.5789,   19.2486),
    "Spa":            (50.4372,    5.9714),
    "Zandvoort":      (52.3888,    4.5407),
    "Monza":          (45.6156,    9.2811),
    "Baku":           (40.3724,   49.8533),
    "Singapore":      (1.2914,   103.8640),
    "Suzuka":         (34.8431,  136.5410),
    "Shanghai":       (31.3389,  121.2200),
    "Austin":         (30.1328,  -97.6411),
    "Mexico City":    (19.4042,  -99.0907),
    "Sao Paulo":      (-23.7036, -46.6997),
    "Las Vegas":      (36.1146, -115.1728),
    "Lusail":         (25.4900,   51.4542),
    "Abu Dhabi":      (24.4672,   54.6031),
    "Portimao":       (37.2274,   -8.6270),
    "Istanbul":       (40.9517,   29.4050),
    "Mugello":        (43.9975,   11.3719),
    "Nurburgring":    (50.3356,    6.9475),
    "Bahrain (Outer)":(26.0350,   50.5120),
}

# ── Catalogue complet des courses 2020–2025 ───────────────────
# Format : session_key OpenF1 (None = utiliser FastF1 par nom)
# Les session_key OpenF1 existent pour 2023+
# Pour 2020-2022 : FastF1 récupère via (year, round_number)

ALL_SESSIONS = [

    # ══ 2020 ══ (17 courses — saison COVID, circuits atypiques)
    {"year": 2020, "round": 1,  "gp_name": "Austrian GP",         "circuit": "Spielberg",      "country": "AUT", "date": "2020-07-05", "laps": 71, "track_km": 4.318,  "session_key": None},
    {"year": 2020, "round": 2,  "gp_name": "Styrian GP",          "circuit": "Spielberg",      "country": "AUT", "date": "2020-07-12", "laps": 71, "track_km": 4.318,  "session_key": None},
    {"year": 2020, "round": 3,  "gp_name": "Hungarian GP",        "circuit": "Budapest",       "country": "HUN", "date": "2020-07-19", "laps": 70, "track_km": 4.381,  "session_key": None},
    {"year": 2020, "round": 4,  "gp_name": "British GP",          "circuit": "Silverstone",    "country": "GBR", "date": "2020-08-02", "laps": 52, "track_km": 5.891,  "session_key": None},
    {"year": 2020, "round": 5,  "gp_name": "70th Anniversary GP", "circuit": "Silverstone",    "country": "GBR", "date": "2020-08-09", "laps": 52, "track_km": 5.891,  "session_key": None},
    {"year": 2020, "round": 6,  "gp_name": "Spanish GP",          "circuit": "Barcelona",      "country": "ESP", "date": "2020-08-16", "laps": 66, "track_km": 4.655,  "session_key": None},
    {"year": 2020, "round": 7,  "gp_name": "Belgian GP",          "circuit": "Spa",            "country": "BEL", "date": "2020-08-30", "laps": 44, "track_km": 7.004,  "session_key": None},
    {"year": 2020, "round": 8,  "gp_name": "Italian GP",          "circuit": "Monza",          "country": "ITA", "date": "2020-09-06", "laps": 53, "track_km": 5.793,  "session_key": None},
    {"year": 2020, "round": 9,  "gp_name": "Tuscan GP",           "circuit": "Mugello",        "country": "ITA", "date": "2020-09-13", "laps": 59, "track_km": 5.245,  "session_key": None},
    {"year": 2020, "round": 10, "gp_name": "Russian GP",          "circuit": "Sochi",          "country": "RUS", "date": "2020-09-27", "laps": 53, "track_km": 5.848,  "session_key": None},
    {"year": 2020, "round": 11, "gp_name": "Eifel GP",            "circuit": "Nurburgring",    "country": "DEU", "date": "2020-10-11", "laps": 60, "track_km": 5.148,  "session_key": None},
    {"year": 2020, "round": 12, "gp_name": "Portuguese GP",       "circuit": "Portimao",       "country": "PRT", "date": "2020-10-25", "laps": 66, "track_km": 4.684,  "session_key": None},
    {"year": 2020, "round": 13, "gp_name": "Emilia Romagna GP",   "circuit": "Imola",          "country": "ITA", "date": "2020-11-01", "laps": 63, "track_km": 4.909,  "session_key": None},
    {"year": 2020, "round": 14, "gp_name": "Turkish GP",          "circuit": "Istanbul",       "country": "TUR", "date": "2020-11-15", "laps": 58, "track_km": 5.338,  "session_key": None},
    {"year": 2020, "round": 15, "gp_name": "Bahrain GP",          "circuit": "Sakhir",         "country": "BRN", "date": "2020-11-29", "laps": 57, "track_km": 5.412,  "session_key": None},
    {"year": 2020, "round": 16, "gp_name": "Sakhir GP",           "circuit": "Bahrain (Outer)","country": "BRN", "date": "2020-12-06", "laps": 87, "track_km": 3.543,  "session_key": None},
    {"year": 2020, "round": 17, "gp_name": "Abu Dhabi GP",        "circuit": "Abu Dhabi",      "country": "UAE", "date": "2020-12-13", "laps": 55, "track_km": 5.554,  "session_key": None},

    # ══ 2021 ══ (22 courses)
    {"year": 2021, "round": 1,  "gp_name": "Bahrain GP",          "circuit": "Sakhir",         "country": "BRN", "date": "2021-03-28", "laps": 56, "track_km": 5.412,  "session_key": None},
    {"year": 2021, "round": 2,  "gp_name": "Emilia Romagna GP",   "circuit": "Imola",          "country": "ITA", "date": "2021-04-18", "laps": 63, "track_km": 4.909,  "session_key": None},
    {"year": 2021, "round": 3,  "gp_name": "Portuguese GP",       "circuit": "Portimao",       "country": "PRT", "date": "2021-05-02", "laps": 66, "track_km": 4.684,  "session_key": None},
    {"year": 2021, "round": 4,  "gp_name": "Spanish GP",          "circuit": "Barcelona",      "country": "ESP", "date": "2021-05-09", "laps": 66, "track_km": 4.655,  "session_key": None},
    {"year": 2021, "round": 5,  "gp_name": "Monaco GP",           "circuit": "Monaco",         "country": "MCO", "date": "2021-05-23", "laps": 78, "track_km": 3.337,  "session_key": None},
    {"year": 2021, "round": 6,  "gp_name": "Azerbaijan GP",       "circuit": "Baku",           "country": "AZE", "date": "2021-06-06", "laps": 51, "track_km": 6.003,  "session_key": None},
    {"year": 2021, "round": 7,  "gp_name": "French GP",           "circuit": "Paul Ricard",    "country": "FRA", "date": "2021-06-20", "laps": 53, "track_km": 5.842,  "session_key": None},
    {"year": 2021, "round": 8,  "gp_name": "Styrian GP",          "circuit": "Spielberg",      "country": "AUT", "date": "2021-06-27", "laps": 71, "track_km": 4.318,  "session_key": None},
    {"year": 2021, "round": 9,  "gp_name": "Austrian GP",         "circuit": "Spielberg",      "country": "AUT", "date": "2021-07-04", "laps": 71, "track_km": 4.318,  "session_key": None},
    {"year": 2021, "round": 10, "gp_name": "British GP",          "circuit": "Silverstone",    "country": "GBR", "date": "2021-07-18", "laps": 52, "track_km": 5.891,  "session_key": None},
    {"year": 2021, "round": 11, "gp_name": "Hungarian GP",        "circuit": "Budapest",       "country": "HUN", "date": "2021-08-01", "laps": 70, "track_km": 4.381,  "session_key": None},
    {"year": 2021, "round": 12, "gp_name": "Belgian GP",          "circuit": "Spa",            "country": "BEL", "date": "2021-08-29", "laps": 44, "track_km": 7.004,  "session_key": None},
    {"year": 2021, "round": 13, "gp_name": "Dutch GP",            "circuit": "Zandvoort",      "country": "NLD", "date": "2021-09-05", "laps": 72, "track_km": 4.259,  "session_key": None},
    {"year": 2021, "round": 14, "gp_name": "Italian GP",          "circuit": "Monza",          "country": "ITA", "date": "2021-09-12", "laps": 53, "track_km": 5.793,  "session_key": None},
    {"year": 2021, "round": 15, "gp_name": "Russian GP",          "circuit": "Sochi",          "country": "RUS", "date": "2021-09-26", "laps": 53, "track_km": 5.848,  "session_key": None},
    {"year": 2021, "round": 16, "gp_name": "Turkish GP",          "circuit": "Istanbul",       "country": "TUR", "date": "2021-10-10", "laps": 58, "track_km": 5.338,  "session_key": None},
    {"year": 2021, "round": 17, "gp_name": "US GP",               "circuit": "Austin",         "country": "USA", "date": "2021-10-24", "laps": 56, "track_km": 5.513,  "session_key": None},
    {"year": 2021, "round": 18, "gp_name": "Mexico City GP",      "circuit": "Mexico City",    "country": "MEX", "date": "2021-11-07", "laps": 71, "track_km": 4.304,  "session_key": None},
    {"year": 2021, "round": 19, "gp_name": "Sao Paulo GP",        "circuit": "Sao Paulo",      "country": "BRA", "date": "2021-11-14", "laps": 71, "track_km": 4.309,  "session_key": None},
    {"year": 2021, "round": 20, "gp_name": "Qatar GP",            "circuit": "Lusail",         "country": "QAT", "date": "2021-11-21", "laps": 57, "track_km": 5.380,  "session_key": None},
    {"year": 2021, "round": 21, "gp_name": "Saudi Arabia GP",     "circuit": "Jeddah",         "country": "SAU", "date": "2021-12-05", "laps": 50, "track_km": 6.174,  "session_key": None},
    {"year": 2021, "round": 22, "gp_name": "Abu Dhabi GP",        "circuit": "Abu Dhabi",      "country": "UAE", "date": "2021-12-12", "laps": 58, "track_km": 5.554,  "session_key": None},

    # ══ 2022 ══ (22 courses)
    {"year": 2022, "round": 1,  "gp_name": "Bahrain GP",          "circuit": "Sakhir",         "country": "BRN", "date": "2022-03-20", "laps": 57, "track_km": 5.412,  "session_key": None},
    {"year": 2022, "round": 2,  "gp_name": "Saudi Arabia GP",     "circuit": "Jeddah",         "country": "SAU", "date": "2022-03-27", "laps": 50, "track_km": 6.174,  "session_key": None},
    {"year": 2022, "round": 3,  "gp_name": "Australian GP",       "circuit": "Melbourne",      "country": "AUS", "date": "2022-04-10", "laps": 58, "track_km": 5.278,  "session_key": None},
    {"year": 2022, "round": 4,  "gp_name": "Emilia Romagna GP",   "circuit": "Imola",          "country": "ITA", "date": "2022-04-24", "laps": 63, "track_km": 4.909,  "session_key": None},
    {"year": 2022, "round": 5,  "gp_name": "Miami GP",            "circuit": "Miami",          "country": "USA", "date": "2022-05-08", "laps": 57, "track_km": 5.412,  "session_key": None},
    {"year": 2022, "round": 6,  "gp_name": "Spanish GP",          "circuit": "Barcelona",      "country": "ESP", "date": "2022-05-22", "laps": 66, "track_km": 4.655,  "session_key": None},
    {"year": 2022, "round": 7,  "gp_name": "Monaco GP",           "circuit": "Monaco",         "country": "MCO", "date": "2022-05-29", "laps": 78, "track_km": 3.337,  "session_key": None},
    {"year": 2022, "round": 8,  "gp_name": "Azerbaijan GP",       "circuit": "Baku",           "country": "AZE", "date": "2022-06-12", "laps": 51, "track_km": 6.003,  "session_key": None},
    {"year": 2022, "round": 9,  "gp_name": "Canadian GP",         "circuit": "Montreal",       "country": "CAN", "date": "2022-06-19", "laps": 70, "track_km": 4.361,  "session_key": None},
    {"year": 2022, "round": 10, "gp_name": "British GP",          "circuit": "Silverstone",    "country": "GBR", "date": "2022-07-03", "laps": 52, "track_km": 5.891,  "session_key": None},
    {"year": 2022, "round": 11, "gp_name": "Austrian GP",         "circuit": "Spielberg",      "country": "AUT", "date": "2022-07-10", "laps": 71, "track_km": 4.318,  "session_key": None},
    {"year": 2022, "round": 12, "gp_name": "French GP",           "circuit": "Paul Ricard",    "country": "FRA", "date": "2022-07-24", "laps": 53, "track_km": 5.842,  "session_key": None},
    {"year": 2022, "round": 13, "gp_name": "Hungarian GP",        "circuit": "Budapest",       "country": "HUN", "date": "2022-07-31", "laps": 70, "track_km": 4.381,  "session_key": None},
    {"year": 2022, "round": 14, "gp_name": "Belgian GP",          "circuit": "Spa",            "country": "BEL", "date": "2022-08-28", "laps": 44, "track_km": 7.004,  "session_key": None},
    {"year": 2022, "round": 15, "gp_name": "Dutch GP",            "circuit": "Zandvoort",      "country": "NLD", "date": "2022-09-04", "laps": 72, "track_km": 4.259,  "session_key": None},
    {"year": 2022, "round": 16, "gp_name": "Italian GP",          "circuit": "Monza",          "country": "ITA", "date": "2022-09-11", "laps": 53, "track_km": 5.793,  "session_key": None},
    {"year": 2022, "round": 17, "gp_name": "Singapore GP",        "circuit": "Singapore",      "country": "SGP", "date": "2022-10-02", "laps": 61, "track_km": 4.940,  "session_key": None},
    {"year": 2022, "round": 18, "gp_name": "Japanese GP",         "circuit": "Suzuka",         "country": "JPN", "date": "2022-10-09", "laps": 53, "track_km": 5.807,  "session_key": None},
    {"year": 2022, "round": 19, "gp_name": "US GP",               "circuit": "Austin",         "country": "USA", "date": "2022-10-23", "laps": 56, "track_km": 5.513,  "session_key": None},
    {"year": 2022, "round": 20, "gp_name": "Mexico City GP",      "circuit": "Mexico City",    "country": "MEX", "date": "2022-11-06", "laps": 71, "track_km": 4.304,  "session_key": None},
    {"year": 2022, "round": 21, "gp_name": "Sao Paulo GP",        "circuit": "Sao Paulo",      "country": "BRA", "date": "2022-11-13", "laps": 71, "track_km": 4.309,  "session_key": None},
    {"year": 2022, "round": 22, "gp_name": "Abu Dhabi GP",        "circuit": "Abu Dhabi",      "country": "UAE", "date": "2022-11-20", "laps": 58, "track_km": 5.554,  "session_key": None},

    # ══ 2023 ══ (22 courses — OpenF1 disponible)
    {"year": 2023, "round": 1,  "gp_name": "Bahrain GP",          "circuit": "Sakhir",         "country": "BRN", "date": "2023-03-05", "laps": 57, "track_km": 5.412,  "session_key": None},
    {"year": 2023, "round": 2,  "gp_name": "Saudi Arabia GP",     "circuit": "Jeddah",         "country": "SAU", "date": "2023-03-19", "laps": 50, "track_km": 6.174,  "session_key": None},
    {"year": 2023, "round": 3,  "gp_name": "Australian GP",       "circuit": "Melbourne",      "country": "AUS", "date": "2023-04-02", "laps": 58, "track_km": 5.278,  "session_key": None},
    {"year": 2023, "round": 4,  "gp_name": "Azerbaijan GP",       "circuit": "Baku",           "country": "AZE", "date": "2023-04-30", "laps": 51, "track_km": 6.003,  "session_key": None},
    {"year": 2023, "round": 5,  "gp_name": "Miami GP",            "circuit": "Miami",          "country": "USA", "date": "2023-05-07", "laps": 57, "track_km": 5.412,  "session_key": None},
    {"year": 2023, "round": 6,  "gp_name": "Monaco GP",           "circuit": "Monaco",         "country": "MCO", "date": "2023-05-28", "laps": 78, "track_km": 3.337,  "session_key": None},
    {"year": 2023, "round": 7,  "gp_name": "Spanish GP",          "circuit": "Barcelona",      "country": "ESP", "date": "2023-06-04", "laps": 66, "track_km": 4.655,  "session_key": None},
    {"year": 2023, "round": 8,  "gp_name": "Canadian GP",         "circuit": "Montreal",       "country": "CAN", "date": "2023-06-18", "laps": 70, "track_km": 4.361,  "session_key": None},
    {"year": 2023, "round": 9,  "gp_name": "Austrian GP",         "circuit": "Spielberg",      "country": "AUT", "date": "2023-07-02", "laps": 71, "track_km": 4.318,  "session_key": None},
    {"year": 2023, "round": 10, "gp_name": "British GP",          "circuit": "Silverstone",    "country": "GBR", "date": "2023-07-09", "laps": 52, "track_km": 5.891,  "session_key": None},
    {"year": 2023, "round": 11, "gp_name": "Hungarian GP",        "circuit": "Budapest",       "country": "HUN", "date": "2023-07-23", "laps": 70, "track_km": 4.381,  "session_key": None},
    {"year": 2023, "round": 12, "gp_name": "Belgian GP",          "circuit": "Spa",            "country": "BEL", "date": "2023-07-30", "laps": 44, "track_km": 7.004,  "session_key": None},
    {"year": 2023, "round": 13, "gp_name": "Dutch GP",            "circuit": "Zandvoort",      "country": "NLD", "date": "2023-08-27", "laps": 72, "track_km": 4.259,  "session_key": None},
    {"year": 2023, "round": 14, "gp_name": "Italian GP",          "circuit": "Monza",          "country": "ITA", "date": "2023-09-03", "laps": 51, "track_km": 5.793,  "session_key": None},
    {"year": 2023, "round": 15, "gp_name": "Singapore GP",        "circuit": "Singapore",      "country": "SGP", "date": "2023-09-17", "laps": 61, "track_km": 4.940,  "session_key": None},
    {"year": 2023, "round": 16, "gp_name": "Japanese GP",         "circuit": "Suzuka",         "country": "JPN", "date": "2023-09-24", "laps": 53, "track_km": 5.807,  "session_key": None},
    {"year": 2023, "round": 17, "gp_name": "Qatar GP",            "circuit": "Lusail",         "country": "QAT", "date": "2023-10-08", "laps": 57, "track_km": 5.380,  "session_key": None},
    {"year": 2023, "round": 18, "gp_name": "US GP",               "circuit": "Austin",         "country": "USA", "date": "2023-10-22", "laps": 56, "track_km": 5.513,  "session_key": None},
    {"year": 2023, "round": 19, "gp_name": "Mexico City GP",      "circuit": "Mexico City",    "country": "MEX", "date": "2023-10-29", "laps": 71, "track_km": 4.304,  "session_key": None},
    {"year": 2023, "round": 20, "gp_name": "Sao Paulo GP",        "circuit": "Sao Paulo",      "country": "BRA", "date": "2023-11-05", "laps": 71, "track_km": 4.309,  "session_key": None},
    {"year": 2023, "round": 21, "gp_name": "Las Vegas GP",        "circuit": "Las Vegas",      "country": "USA", "date": "2023-11-18", "laps": 50, "track_km": 6.201,  "session_key": None},
    {"year": 2023, "round": 22, "gp_name": "Abu Dhabi GP",        "circuit": "Abu Dhabi",      "country": "UAE", "date": "2023-11-26", "laps": 58, "track_km": 5.554,  "session_key": None},

    # ══ 2024 ══ (24 courses — OpenF1)
    {"year": 2024, "round": 1,  "gp_name": "Bahrain GP",          "circuit": "Sakhir",         "country": "BRN", "date": "2024-03-02", "laps": 57, "track_km": 5.412,  "session_key": 9473},
    {"year": 2024, "round": 2,  "gp_name": "Saudi Arabia GP",     "circuit": "Jeddah",         "country": "SAU", "date": "2024-03-09", "laps": 50, "track_km": 6.174,  "session_key": None},
    {"year": 2024, "round": 3,  "gp_name": "Australian GP",       "circuit": "Melbourne",      "country": "AUS", "date": "2024-03-24", "laps": 58, "track_km": 5.278,  "session_key": None},
    {"year": 2024, "round": 4,  "gp_name": "Japanese GP",         "circuit": "Suzuka",         "country": "JPN", "date": "2024-04-07", "laps": 53, "track_km": 5.807,  "session_key": None},
    {"year": 2024, "round": 5,  "gp_name": "Chinese GP",          "circuit": "Shanghai",       "country": "CHN", "date": "2024-04-21", "laps": 56, "track_km": 5.451,  "session_key": None},
    {"year": 2024, "round": 6,  "gp_name": "Miami GP",            "circuit": "Miami",          "country": "USA", "date": "2024-05-05", "laps": 57, "track_km": 5.412,  "session_key": None},
    {"year": 2024, "round": 7,  "gp_name": "Emilia Romagna GP",   "circuit": "Imola",          "country": "ITA", "date": "2024-05-19", "laps": 63, "track_km": 4.909,  "session_key": None},
    {"year": 2024, "round": 8,  "gp_name": "Monaco GP",           "circuit": "Monaco",         "country": "MCO", "date": "2024-05-26", "laps": 78, "track_km": 3.337,  "session_key": None},
    {"year": 2024, "round": 9,  "gp_name": "Canadian GP",         "circuit": "Montreal",       "country": "CAN", "date": "2024-06-09", "laps": 70, "track_km": 4.361,  "session_key": None},
    {"year": 2024, "round": 10, "gp_name": "Spanish GP",          "circuit": "Barcelona",      "country": "ESP", "date": "2024-06-23", "laps": 66, "track_km": 4.655,  "session_key": None},
    {"year": 2024, "round": 11, "gp_name": "Austrian GP",         "circuit": "Spielberg",      "country": "AUT", "date": "2024-06-30", "laps": 71, "track_km": 4.318,  "session_key": None},
    {"year": 2024, "round": 12, "gp_name": "British GP",          "circuit": "Silverstone",    "country": "GBR", "date": "2024-07-07", "laps": 52, "track_km": 5.891,  "session_key": None},
    {"year": 2024, "round": 13, "gp_name": "Hungarian GP",        "circuit": "Budapest",       "country": "HUN", "date": "2024-07-21", "laps": 70, "track_km": 4.381,  "session_key": None},
    {"year": 2024, "round": 14, "gp_name": "Belgian GP",          "circuit": "Spa",            "country": "BEL", "date": "2024-07-28", "laps": 44, "track_km": 7.004,  "session_key": None},
    {"year": 2024, "round": 15, "gp_name": "Dutch GP",            "circuit": "Zandvoort",      "country": "NLD", "date": "2024-08-25", "laps": 72, "track_km": 4.259,  "session_key": None},
    {"year": 2024, "round": 16, "gp_name": "Italian GP",          "circuit": "Monza",          "country": "ITA", "date": "2024-09-01", "laps": 53, "track_km": 5.793,  "session_key": None},
    {"year": 2024, "round": 17, "gp_name": "Azerbaijan GP",       "circuit": "Baku",           "country": "AZE", "date": "2024-09-15", "laps": 51, "track_km": 6.003,  "session_key": None},
    {"year": 2024, "round": 18, "gp_name": "Singapore GP",        "circuit": "Singapore",      "country": "SGP", "date": "2024-09-22", "laps": 61, "track_km": 4.940,  "session_key": None},
    {"year": 2024, "round": 19, "gp_name": "US GP",               "circuit": "Austin",         "country": "USA", "date": "2024-10-20", "laps": 56, "track_km": 5.513,  "session_key": None},
    {"year": 2024, "round": 20, "gp_name": "Mexico City GP",      "circuit": "Mexico City",    "country": "MEX", "date": "2024-10-27", "laps": 71, "track_km": 4.304,  "session_key": None},
    {"year": 2024, "round": 21, "gp_name": "Sao Paulo GP",        "circuit": "Sao Paulo",      "country": "BRA", "date": "2024-11-03", "laps": 69, "track_km": 4.309,  "session_key": None},
    {"year": 2024, "round": 22, "gp_name": "Las Vegas GP",        "circuit": "Las Vegas",      "country": "USA", "date": "2024-11-23", "laps": 50, "track_km": 6.201,  "session_key": None},
    {"year": 2024, "round": 23, "gp_name": "Qatar GP",            "circuit": "Lusail",         "country": "QAT", "date": "2024-12-01", "laps": 57, "track_km": 5.380,  "session_key": None},
    {"year": 2024, "round": 24, "gp_name": "Abu Dhabi GP",        "circuit": "Abu Dhabi",      "country": "UAE", "date": "2024-12-08", "laps": 58, "track_km": 5.554,  "session_key": None},

    # ══ 2025 ══ (24 courses — OpenF1, saison en cours)
    {"year": 2025, "round": 1,  "gp_name": "Australian GP",       "circuit": "Melbourne",      "country": "AUS", "date": "2025-03-16", "laps": 58, "track_km": 5.278,  "session_key": None},
    {"year": 2025, "round": 2,  "gp_name": "Chinese GP",          "circuit": "Shanghai",       "country": "CHN", "date": "2025-03-23", "laps": 56, "track_km": 5.451,  "session_key": None},
    {"year": 2025, "round": 3,  "gp_name": "Japanese GP",         "circuit": "Suzuka",         "country": "JPN", "date": "2025-04-06", "laps": 53, "track_km": 5.807,  "session_key": None},
    {"year": 2025, "round": 4,  "gp_name": "Bahrain GP",          "circuit": "Sakhir",         "country": "BRN", "date": "2025-04-13", "laps": 57, "track_km": 5.412,  "session_key": None},
    {"year": 2025, "round": 5,  "gp_name": "Saudi Arabia GP",     "circuit": "Jeddah",         "country": "SAU", "date": "2025-04-20", "laps": 50, "track_km": 6.174,  "session_key": None},
    {"year": 2025, "round": 6,  "gp_name": "Miami GP",            "circuit": "Miami",          "country": "USA", "date": "2025-05-04", "laps": 57, "track_km": 5.412,  "session_key": None},
    {"year": 2025, "round": 7,  "gp_name": "Emilia Romagna GP",   "circuit": "Imola",          "country": "ITA", "date": "2025-05-18", "laps": 63, "track_km": 4.909,  "session_key": None},
    {"year": 2025, "round": 8,  "gp_name": "Monaco GP",           "circuit": "Monaco",         "country": "MCO", "date": "2025-05-25", "laps": 78, "track_km": 3.337,  "session_key": None},
    {"year": 2025, "round": 9,  "gp_name": "Spanish GP",          "circuit": "Barcelona",      "country": "ESP", "date": "2025-06-01", "laps": 66, "track_km": 4.655,  "session_key": None},
    {"year": 2025, "round": 10, "gp_name": "Canadian GP",         "circuit": "Montreal",       "country": "CAN", "date": "2025-06-15", "laps": 70, "track_km": 4.361,  "session_key": None},
    {"year": 2025, "round": 11, "gp_name": "Austrian GP",         "circuit": "Spielberg",      "country": "AUT", "date": "2025-06-29", "laps": 71, "track_km": 4.318,  "session_key": None},
    {"year": 2025, "round": 12, "gp_name": "British GP",          "circuit": "Silverstone",    "country": "GBR", "date": "2025-07-06", "laps": 52, "track_km": 5.891,  "session_key": None},
    {"year": 2025, "round": 13, "gp_name": "Belgian GP",          "circuit": "Spa",            "country": "BEL", "date": "2025-07-27", "laps": 44, "track_km": 7.004,  "session_key": None},
    {"year": 2025, "round": 14, "gp_name": "Hungarian GP",        "circuit": "Budapest",       "country": "HUN", "date": "2025-08-03", "laps": 70, "track_km": 4.381,  "session_key": None},
    {"year": 2025, "round": 15, "gp_name": "Dutch GP",            "circuit": "Zandvoort",      "country": "NLD", "date": "2025-08-31", "laps": 72, "track_km": 4.259,  "session_key": None},
    {"year": 2025, "round": 16, "gp_name": "Italian GP",          "circuit": "Monza",          "country": "ITA", "date": "2025-09-07", "laps": 53, "track_km": 5.793,  "session_key": None},
    {"year": 2025, "round": 17, "gp_name": "Azerbaijan GP",       "circuit": "Baku",           "country": "AZE", "date": "2025-09-21", "laps": 51, "track_km": 6.003,  "session_key": None},
    {"year": 2025, "round": 18, "gp_name": "Singapore GP",        "circuit": "Singapore",      "country": "SGP", "date": "2025-10-05", "laps": 61, "track_km": 4.940,  "session_key": None},
    {"year": 2025, "round": 19, "gp_name": "US GP",               "circuit": "Austin",         "country": "USA", "date": "2025-10-19", "laps": 56, "track_km": 5.513,  "session_key": None},
    {"year": 2025, "round": 20, "gp_name": "Mexico City GP",      "circuit": "Mexico City",    "country": "MEX", "date": "2025-10-26", "laps": 71, "track_km": 4.304,  "session_key": None},
    {"year": 2025, "round": 21, "gp_name": "Sao Paulo GP",        "circuit": "Sao Paulo",      "country": "BRA", "date": "2025-11-09", "laps": 71, "track_km": 4.309,  "session_key": None},
    {"year": 2025, "round": 22, "gp_name": "Las Vegas GP",        "circuit": "Las Vegas",      "country": "USA", "date": "2025-11-22", "laps": 50, "track_km": 6.201,  "session_key": None},
    {"year": 2025, "round": 23, "gp_name": "Qatar GP",            "circuit": "Lusail",         "country": "QAT", "date": "2025-11-30", "laps": 57, "track_km": 5.380,  "session_key": None},
    {"year": 2025, "round": 24, "gp_name": "Abu Dhabi GP",        "circuit": "Abu Dhabi",      "country": "UAE", "date": "2025-12-07", "laps": 58, "track_km": 5.554,  "session_key": None},
]


import pandas as pd

def get_all_sessions() -> pd.DataFrame:
    """Retourne le catalogue complet 2020-2025 sous forme DataFrame."""
    return pd.DataFrame(ALL_SESSIONS)

def get_sessions_by_year(year: int) -> pd.DataFrame:
    """Filtre les sessions par année."""
    df = pd.DataFrame(ALL_SESSIONS)
    return df[df["year"] == year].reset_index(drop=True)

def get_session_by_key(session_key: int) -> dict:
    """Retourne les infos d'une session par session_key OpenF1."""
    for s in ALL_SESSIONS:
        if s["session_key"] == session_key:
            return s
    return {}

def get_session_by_round(year: int, round_number: int) -> dict:
    """Retourne les infos d'une session par année + numéro de manche."""
    for s in ALL_SESSIONS:
        if s["year"] == year and s["round"] == round_number:
            return s
    return {}

def available_years() -> list:
    return sorted(set(s["year"] for s in ALL_SESSIONS))

def total_sessions() -> int:
    return len(ALL_SESSIONS)
