"""
mock_data.py — F1 Data Hub · Projet 3 · Wild Code School
════════════════════════════════════════════════════════
Données simulées réalistes pour les 6 GPs 2024.
Basculement en production : voir api_fetcher.py

Chaque GP a :
  - Des temps de base réels (référencés sur les qualifications 2024)
  - Des stratégies pneus différenciées
  - Des pit stops adaptés au circuit
  - Des conditions météo spécifiques
"""

import pandas as pd
import numpy as np
import math as _math


def _safe_int(val, default: int = 9473) -> int:
    """Convertit val (None, NaN, float, int) en int — sans lever d'exception."""
    if val is None:
        return default
    try:
        f = float(val)
        return default if _math.isnan(f) else int(f)
    except (TypeError, ValueError):
        return default
from datetime import datetime, timedelta
import re as _re


# ════════════════════════════════════════════════════════════════
# Utilitaires couleurs
# ════════════════════════════════════════════════════════════════

def _parse_color(color: str):
    color = color.strip()
    if color.startswith("#"):
        h = color.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    elif color.startswith("rgb"):
        nums = _re.findall(r"[\d.]+", color)
        return int(float(nums[0])), int(float(nums[1])), int(float(nums[2]))
    raise ValueError(f"Format couleur non reconnu : {color!r}")

def hex_to_rgb(color: str) -> str:
    r, g, b = _parse_color(color)
    return f"rgb({r}, {g}, {b})"

def hex_to_rgba(color: str, alpha: float = 0.33) -> str:
    r, g, b = _parse_color(color)
    return f"rgba({r}, {g}, {b}, {alpha})"


# ════════════════════════════════════════════════════════════════
# Données de référence pilotes & équipes
# ════════════════════════════════════════════════════════════════

DRIVERS_2024 = [
    {"acronym": "VER", "name": "Max Verstappen",   "team": "Red Bull Racing", "color": "rgb(54, 113, 198)"},
    {"acronym": "PER", "name": "Sergio Perez",      "team": "Red Bull Racing", "color": "rgb(54, 113, 198)"},
    {"acronym": "LEC", "name": "Charles Leclerc",   "team": "Ferrari",         "color": "rgb(232, 0, 45)"},
    {"acronym": "SAI", "name": "Carlos Sainz",      "team": "Ferrari",         "color": "rgb(232, 0, 45)"},
    {"acronym": "HAM", "name": "Lewis Hamilton",    "team": "Mercedes",        "color": "rgb(39, 244, 210)"},
    {"acronym": "RUS", "name": "George Russell",    "team": "Mercedes",        "color": "rgb(39, 244, 210)"},
    {"acronym": "NOR", "name": "Lando Norris",      "team": "McLaren",         "color": "rgb(255, 128, 0)"},
    {"acronym": "PIA", "name": "Oscar Piastri",     "team": "McLaren",         "color": "rgb(255, 128, 0)"},
    {"acronym": "ALO", "name": "Fernando Alonso",   "team": "Aston Martin",    "color": "rgb(53, 140, 117)"},
    {"acronym": "STR", "name": "Lance Stroll",      "team": "Aston Martin",    "color": "rgb(53, 140, 117)"},
]

SESSIONS_2024 = [
    {"session_key": 9473, "gp_name": "Bahrain GP",      "circuit": "Sakhir",    "country": "BRN", "date": "2024-03-02", "laps": 57, "track_km": 5.412},
    {"session_key": 9495, "gp_name": "Saudi Arabia GP", "circuit": "Jeddah",    "country": "SAU", "date": "2024-03-09", "laps": 50, "track_km": 6.174},
    {"session_key": 9521, "gp_name": "Australian GP",   "circuit": "Melbourne", "country": "AUS", "date": "2024-03-24", "laps": 58, "track_km": 5.278},
    {"session_key": 9548, "gp_name": "Japanese GP",     "circuit": "Suzuka",    "country": "JPN", "date": "2024-04-07", "laps": 53, "track_km": 5.807},
    {"session_key": 9580, "gp_name": "Chinese GP",      "circuit": "Shanghai",  "country": "CHN", "date": "2024-04-21", "laps": 56, "track_km": 5.451},
    {"session_key": 9612, "gp_name": "Miami GP",        "circuit": "Miami",     "country": "USA", "date": "2024-05-05", "laps": 57, "track_km": 5.412},
]

CIRCUIT_COORDS = {
    "Sakhir":    (26.0325,  50.5106),
    "Jeddah":    (21.6319,  39.1044),
    "Melbourne": (-37.8497, 144.968),
    "Suzuka":    (34.8431,  136.541),
    "Shanghai":  (31.3389,  121.220),
    "Miami":     (25.9581, -80.2389),
}

TEAM_COLORS = {
    "Red Bull Racing": "rgb(54, 113, 198)",
    "Ferrari":         "rgb(232, 0, 45)",
    "Mercedes":        "rgb(39, 244, 210)",
    "McLaren":         "rgb(255, 128, 0)",
    "Aston Martin":    "rgb(53, 140, 117)",
}

COMPOUND_COLORS = {
    "SOFT":   "rgb(232, 0, 45)",
    "MEDIUM": "rgb(255, 242, 0)",
    "HARD":   "rgb(255, 255, 255)",
    "INTER":  "rgb(57, 181, 74)",
    "WET":    "rgb(0, 103, 255)",
}

DRIVER_COLORS = {d["acronym"]: d["color"] for d in DRIVERS_2024}


# ════════════════════════════════════════════════════════════════
# Paramètres réalistes par session
# Temps de base : inspirés des meilleures qualifications 2024
# Stratégies : fidèles aux vraies stratégies de course
# ════════════════════════════════════════════════════════════════

SESSION_PARAMS = {

    9473: {  # ── BAHRAIN — Sakhir · 57 tours
        "base_times": {
            "VER": 93.5, "LEC": 93.9, "SAI": 94.0, "NOR": 94.3,
            "PER": 94.8, "HAM": 94.1, "RUS": 94.4, "ALO": 94.5,
            "PIA": 94.6, "STR": 95.2,
        },
        "strategies": {
            "VER": ["SOFT"]*14 + ["MEDIUM"]*21 + ["HARD"]*22,
            "LEC": ["SOFT"]*12 + ["MEDIUM"]*24 + ["HARD"]*21,
            "SAI": ["SOFT"]*11 + ["MEDIUM"]*20 + ["HARD"]*26,
            "NOR": ["SOFT"]*16 + ["HARD"]*41,
            "PER": ["SOFT"]*14 + ["MEDIUM"]*21 + ["HARD"]*22,
            "HAM": ["MEDIUM"]*29 + ["HARD"]*28,
            "RUS": ["SOFT"]*13 + ["MEDIUM"]*26 + ["HARD"]*18,
            "ALO": ["MEDIUM"]*27 + ["HARD"]*30,
            "PIA": ["MEDIUM"]*29 + ["HARD"]*28,
            "STR": ["MEDIUM"]*24 + ["HARD"]*33,
        },
        "pit_laps": {
            "VER": [14, 35], "LEC": [12, 36], "SAI": [11, 31],
            "NOR": [16],     "PER": [14, 35], "HAM": [29],
            "RUS": [13, 39], "ALO": [27],     "PIA": [29], "STR": [24],
        },
        "deg_factor": 1.0,
        "weather_temp": 28, "track_temp": 42, "wind_speed": 12,
        "race_date": "2024-03-02",
        "desc": "Course sèche · fort vent de sable en fin de journée",
        "vmax_base": 305,
    },

    9495: {  # ── SAUDI ARABIA — Jeddah · 50 tours
        # Jeddah : circuit rapide, long, peu de dégradation
        "base_times": {
            "VER": 88.2, "LEC": 88.6, "SAI": 88.7, "NOR": 89.0,
            "PER": 89.4, "HAM": 88.9, "RUS": 89.1, "ALO": 89.3,
            "PIA": 89.2, "STR": 90.0,
        },
        "strategies": {
            "VER": ["MEDIUM"]*20 + ["HARD"]*30,
            "LEC": ["SOFT"]*10 + ["HARD"]*40,
            "SAI": ["SOFT"]*11 + ["HARD"]*39,
            "NOR": ["MEDIUM"]*22 + ["HARD"]*28,
            "PER": ["MEDIUM"]*19 + ["HARD"]*31,
            "HAM": ["MEDIUM"]*21 + ["HARD"]*29,
            "RUS": ["SOFT"]*10 + ["MEDIUM"]*18 + ["HARD"]*22,
            "ALO": ["MEDIUM"]*23 + ["HARD"]*27,
            "PIA": ["MEDIUM"]*20 + ["HARD"]*30,
            "STR": ["HARD"]*50,
        },
        "pit_laps": {
            "VER": [20],     "LEC": [10],     "SAI": [11],
            "NOR": [22],     "PER": [19],     "HAM": [21],
            "RUS": [10, 28], "ALO": [23],     "PIA": [20], "STR": [],
        },
        "deg_factor": 0.7,   # Dégradation faible — asphalte lisse
        "weather_temp": 32, "track_temp": 48, "wind_speed": 8,
        "race_date": "2024-03-09",
        "desc": "Circuit urbain nocturne · 1 arrêt dominant · asphalte neuf",
        "vmax_base": 322,    # Vitesse de pointe élevée (longue ligne droite)
    },

    9521: {  # ── AUSTRALIA — Melbourne · 58 tours
        # Melbourne : circuit technique, 2 arrêts fréquents, voiture de sécurité possible
        "base_times": {
            "VER": 80.2, "LEC": 80.5, "SAI": 80.4, "NOR": 80.8,
            "PER": 81.3, "HAM": 80.9, "RUS": 81.0, "ALO": 81.1,
            "PIA": 81.2, "STR": 81.9,
        },
        "strategies": {
            "VER": ["SOFT"]*16 + ["MEDIUM"]*22 + ["HARD"]*20,
            "LEC": ["SOFT"]*14 + ["MEDIUM"]*23 + ["HARD"]*21,
            "SAI": ["SOFT"]*13 + ["HARD"]*25 + ["MEDIUM"]*20,
            "NOR": ["SOFT"]*15 + ["MEDIUM"]*20 + ["HARD"]*23,
            "PER": ["SOFT"]*16 + ["MEDIUM"]*21 + ["HARD"]*21,
            "HAM": ["MEDIUM"]*26 + ["SOFT"]*10 + ["HARD"]*22,
            "RUS": ["SOFT"]*14 + ["MEDIUM"]*24 + ["HARD"]*20,
            "ALO": ["MEDIUM"]*25 + ["HARD"]*33,
            "PIA": ["SOFT"]*15 + ["MEDIUM"]*22 + ["HARD"]*21,
            "STR": ["MEDIUM"]*24 + ["HARD"]*34,
        },
        "pit_laps": {
            "VER": [16, 38], "LEC": [14, 37], "SAI": [13, 38],
            "NOR": [15, 35], "PER": [16, 37], "HAM": [26, 36],
            "RUS": [14, 38], "ALO": [25],     "PIA": [15, 37], "STR": [24],
        },
        "deg_factor": 1.1,
        "weather_temp": 22, "track_temp": 32, "wind_speed": 18,
        "race_date": "2024-03-24",
        "desc": "Conditions fraîches · risque Safety Car · 2 arrêts optimal",
        "vmax_base": 298,
    },

    9548: {  # ── JAPAN — Suzuka · 53 tours
        # Suzuka : circuit exigeant, fort grip, dégradation pneus élevée
        "base_times": {
            "VER": 91.8, "LEC": 92.1, "SAI": 92.2, "NOR": 92.5,
            "PER": 93.0, "HAM": 92.6, "RUS": 92.7, "ALO": 92.8,
            "PIA": 92.9, "STR": 93.6,
        },
        "strategies": {
            "VER": ["SOFT"]*17 + ["MEDIUM"]*36,
            "LEC": ["SOFT"]*15 + ["MEDIUM"]*38,
            "SAI": ["SOFT"]*14 + ["HARD"]*39,
            "NOR": ["SOFT"]*16 + ["MEDIUM"]*37,
            "PER": ["SOFT"]*16 + ["MEDIUM"]*37,
            "HAM": ["MEDIUM"]*25 + ["HARD"]*28,
            "RUS": ["SOFT"]*15 + ["MEDIUM"]*38,
            "ALO": ["MEDIUM"]*26 + ["HARD"]*27,
            "PIA": ["SOFT"]*16 + ["HARD"]*37,
            "STR": ["MEDIUM"]*24 + ["HARD"]*29,
        },
        "pit_laps": {
            "VER": [17],     "LEC": [15],     "SAI": [14],
            "NOR": [16],     "PER": [16],     "HAM": [25],
            "RUS": [15],     "ALO": [26],     "PIA": [16], "STR": [24],
        },
        "deg_factor": 1.3,   # Dégradation élevée — charges aéro importantes
        "weather_temp": 18, "track_temp": 26, "wind_speed": 10,
        "race_date": "2024-04-07",
        "desc": "Piste rapide et technique · 1 arrêt dominant · forte dégradation",
        "vmax_base": 302,
    },

    9580: {  # ── CHINA — Shanghai · 56 tours
        # Shanghai : circuit polyvalent, retour au calendrier 2024
        "base_times": {
            "VER": 96.5, "LEC": 96.9, "SAI": 97.0, "NOR": 97.2,
            "PER": 97.7, "HAM": 97.1, "RUS": 97.3, "ALO": 97.4,
            "PIA": 97.5, "STR": 98.1,
        },
        "strategies": {
            "VER": ["MEDIUM"]*22 + ["HARD"]*34,
            "LEC": ["SOFT"]*12 + ["MEDIUM"]*20 + ["HARD"]*24,
            "SAI": ["SOFT"]*11 + ["HARD"]*45,
            "NOR": ["MEDIUM"]*23 + ["HARD"]*33,
            "PER": ["MEDIUM"]*21 + ["HARD"]*35,
            "HAM": ["SOFT"]*13 + ["MEDIUM"]*20 + ["HARD"]*23,
            "RUS": ["MEDIUM"]*22 + ["HARD"]*34,
            "ALO": ["HARD"]*28 + ["MEDIUM"]*28,
            "PIA": ["MEDIUM"]*22 + ["HARD"]*34,
            "STR": ["HARD"]*30 + ["MEDIUM"]*26,
        },
        "pit_laps": {
            "VER": [22],     "LEC": [12, 32], "SAI": [11],
            "NOR": [23],     "PER": [21],     "HAM": [13, 33],
            "RUS": [22],     "ALO": [28],     "PIA": [22], "STR": [30],
        },
        "deg_factor": 0.9,
        "weather_temp": 20, "track_temp": 30, "wind_speed": 14,
        "race_date": "2024-04-21",
        "desc": "Retour de Shanghai · légère humidité · sprint weekend",
        "vmax_base": 301,
    },

    9612: {  # ── MIAMI — Miami · 57 tours
        # Miami : chaleur extrême, dégradation maximum, pneus tendres favorisés
        "base_times": {
            "VER": 91.4, "LEC": 91.8, "SAI": 91.9, "NOR": 92.0,
            "PER": 92.5, "HAM": 92.1, "RUS": 92.2, "ALO": 92.3,
            "PIA": 92.1, "STR": 92.9,
        },
        "strategies": {
            "VER": ["SOFT"]*18 + ["MEDIUM"]*19 + ["HARD"]*20,
            "LEC": ["SOFT"]*16 + ["MEDIUM"]*20 + ["HARD"]*21,
            "SAI": ["SOFT"]*15 + ["HARD"]*20 + ["MEDIUM"]*22,
            "NOR": ["SOFT"]*17 + ["MEDIUM"]*20 + ["HARD"]*20,
            "PER": ["SOFT"]*16 + ["MEDIUM"]*20 + ["HARD"]*21,
            "HAM": ["MEDIUM"]*24 + ["SOFT"]*13 + ["HARD"]*20,
            "RUS": ["SOFT"]*16 + ["MEDIUM"]*20 + ["HARD"]*21,
            "ALO": ["MEDIUM"]*22 + ["HARD"]*35,
            "PIA": ["SOFT"]*17 + ["MEDIUM"]*19 + ["HARD"]*21,
            "STR": ["HARD"]*30 + ["MEDIUM"]*27,
        },
        "pit_laps": {
            "VER": [18, 37], "LEC": [16, 36], "SAI": [15, 35],
            "NOR": [17, 37], "PER": [16, 36], "HAM": [24, 37],
            "RUS": [16, 36], "ALO": [22],     "PIA": [17, 36], "STR": [30],
        },
        "deg_factor": 1.6,   # Dégradation max — chaleur 30°C / piste 50°C
        "weather_temp": 30, "track_temp": 50, "wind_speed": 6,
        "race_date": "2024-05-05",
        "desc": "Chaleur extrême · 2 arrêts obligatoires · dégradation record",
        "vmax_base": 308,
    },
}


# ════════════════════════════════════════════════════════════════
# Fonctions de données
# ════════════════════════════════════════════════════════════════

def get_sessions() -> pd.DataFrame:
    return pd.DataFrame(SESSIONS_2024)


def get_laps(session_key: int, n_laps: int = 57,
              year: int = 2024, round_num: int = 1) -> pd.DataFrame:
    """Génère les données de tours pour un GP — réaliste par session."""
    _seed = (_safe_int(session_key) * 31 + year * 100 + round_num) % 99991
    np.random.seed(_seed)

    p          = SESSION_PARAMS.get(_safe_int(session_key), SESSION_PARAMS[9473])
    base_times = p["base_times"]
    strategies = p["strategies"]
    deg_factor = p["deg_factor"]
    vmax_base  = p.get("vmax_base", 305)

    rows = []
    for drv_info in DRIVERS_2024:
        drv   = drv_info["acronym"]
        base  = base_times[drv]
        strat = (strategies[drv] + ["HARD"] * max(20, n_laps))[:n_laps]

        tyre_age  = 0
        prev_cmpd = None

        for lap in range(1, n_laps + 1):
            c = strat[lap - 1]
            if c != prev_cmpd:
                tyre_age = 0
            tyre_age  += 1
            prev_cmpd  = c

            deg         = {"SOFT": 0.045, "MEDIUM": 0.022, "HARD": 0.010}[c] * tyre_age * deg_factor
            fuel_offset = (n_laps - lap) * 0.025
            noise       = np.random.normal(0, 0.12)
            lap_time    = base + deg + fuel_offset * 0.1 + noise

            # Tour lent : Safety Car / trafic (2.5%)
            if np.random.random() < 0.025:
                lap_time += np.random.uniform(3, 10)

            s1 = lap_time * 0.28 + np.random.normal(0, 0.04)
            s2 = lap_time * 0.38 + np.random.normal(0, 0.04)
            s3 = lap_time - s1 - s2

            rows.append({
                "session_key":      session_key,
                "driver":           drv,
                "team":             drv_info["team"],
                "color":            drv_info["color"],
                "lap_number":       lap,
                "lap_time_s":       round(lap_time, 3),
                "sector1_s":        round(s1, 3),
                "sector2_s":        round(s2, 3),
                "sector3_s":        round(s3, 3),
                "compound":         c,
                "tyre_life":        tyre_age,
                "speed_fl_kmh":     round(np.random.normal(vmax_base if drv == "VER" else vmax_base - 4, 4), 1),
                "is_personal_best": False,
            })

    df = pd.DataFrame(rows)
    df["is_personal_best"] = df.groupby("driver")["lap_time_s"].transform(
        lambda x: x == x.cummin()
    )
    return df


def get_pit_stops(session_key: int,
                   year: int = 2024, round_num: int = 1) -> pd.DataFrame:
    """Retourne les pit stops réalistes par session."""
    _seed = (99 + _safe_int(session_key) * 17 + year * 100 + round_num) % 99991
    np.random.seed(_seed)
    p        = SESSION_PARAMS.get(_safe_int(session_key), SESSION_PARAMS[9473])
    pit_laps = p["pit_laps"]

    # Durée pit selon le circuit (Jeddah plus rapide, Bahrain plus lent)
    pit_mean = {9473: 23.5, 9495: 21.8, 9521: 24.2,
                9548: 23.0, 9580: 23.8, 9612: 24.5}.get(session_key, 23.5)

    rows = []
    for drv, laps in pit_laps.items():
        for lap in laps:
            rows.append({
                "session_key":    session_key,
                "driver":         drv,
                "lap_number":     lap,
                "pit_duration_s": round(np.random.normal(pit_mean, 1.0), 2),
                "pit_in_time":    lap * 90.0,
            })
    return pd.DataFrame(rows)


def get_weather(session_key: int, n_points: int = 57,
                year: int = 2024, round_num: int = 1) -> pd.DataFrame:
    """Retourne les données météo simulées par session."""
    _sk = _safe_int(session_key)
    p   = SESSION_PARAMS.get(_sk)

    if p is not None:
        air_base = p["weather_temp"]
        trk_base = p["track_temp"]
        wnd_base = p["wind_speed"]
        _seed    = _sk % 99991
    else:
        _air     = 14 + round_num * 1.3 + (year - 2020) * 0.4
        air_base = round(float(min(42, max(10, _air))), 1)
        trk_base = round(float(min(58, max(15, air_base + 13 + round_num * 0.5))), 1)
        wnd_base = round(float(6 + (round_num % 7) * 1.8), 1)
        _seed    = (year * 1000 + round_num * 37) % 99991

    np.random.seed(_seed)

    try:
        t0 = pd.to_datetime(p["race_date"]).to_pydatetime().replace(hour=14, minute=0)
    except Exception:
        from datetime import timedelta as _td
        t0 = datetime(year, 3, 1, 14, 0) + _td(weeks=int(round_num) - 1)

    rows = []
    for i in range(n_points):
        t = t0 + timedelta(minutes=i * 2)
        rows.append({
            "date":              t,
            "air_temperature":   round(air_base + 3 * np.sin(i / 10) + np.random.normal(0, 0.3), 1),
            "track_temperature": round(trk_base + 5 * np.sin(i / 8)  + np.random.normal(0, 0.5), 1),
            "humidity":          round(max(10, min(95, 40 + 8 * np.cos(i / 12) + np.random.normal(0, 1))), 1),
            "wind_speed":        round(max(0, wnd_base + np.random.normal(0, 2.5)), 1),
            "wind_direction":    int(np.random.normal(180, 35) % 360),
            "rainfall":          0,
        })
    return pd.DataFrame(rows)


def get_telemetry(driver: str, laps: int = 50,
                   year: int = 2024, round_num: int = 1) -> pd.DataFrame:
    vmax = {"VER": 305, "LEC": 302, "HAM": 300, "NOR": 301}.get(driver, 298)
    n    = laps * 20
    t    = np.linspace(0, laps * 94, n)
    thr  = np.clip(np.sin(t * 0.3) * 60 + 60 + np.random.normal(0, 5, n), 0, 100)
    brk  = np.clip(-np.sin(t * 0.3) * 40 + np.random.normal(0, 3, n), 0, 100)
    spd  = vmax * (thr / 100) * 0.8 + 50 + np.random.normal(0, 5, n)
    gear = np.clip(np.round(spd / 40).astype(int), 1, 8)
    return pd.DataFrame({
        "time_s":       t,
        "speed_kmh":    np.round(spd, 1),
        "throttle_pct": np.round(thr, 1),
        "brake_pct":    np.round(brk, 1),
        "gear":         gear,
        "driver":       driver,
    })


# Standings réels par saison (données historiques réelles)
STANDINGS_BY_YEAR = {
    2025: [
        ("NOR","Lando Norris",     "McLaren",         245),
        ("PIA","Oscar Piastri",    "McLaren",         197),
        ("LEC","Charles Leclerc", "Ferrari",         163),
        ("RUS","George Russell",   "Mercedes",        148),
        ("ANT","Andrea Kimi Antonelli","Mercedes",    108),
        ("VER","Max Verstappen",   "Red Bull Racing", 136),
        ("SAI","Carlos Sainz",     "Williams",        114),
        ("HAM","Lewis Hamilton",   "Ferrari",          92),
        ("ALO","Fernando Alonso",  "Aston Martin",     54),
        ("GAS","Pierre Gasly",     "Alpine",           34),
        ("HUL","Nico Hulkenberg",  "Sauber",           28),
        ("TSU","Yuki Tsunoda",     "Red Bull Racing",  26),
        ("LAW","Liam Lawson",      "RB",               18),
        ("STR","Lance Stroll",     "Aston Martin",     14),
        ("BEA","Oliver Bearman",   "Haas",             12),
    ],
    2024: [
        ("VER","Max Verstappen",   "Red Bull Racing", 437),
        ("NOR","Lando Norris",     "McLaren",         374),
        ("LEC","Charles Leclerc", "Ferrari",         356),
        ("PIA","Oscar Piastri",   "McLaren",         292),
        ("SAI","Carlos Sainz",    "Ferrari",         290),
        ("RUS","George Russell",  "Mercedes",        245),
        ("HAM","Lewis Hamilton",  "Mercedes",        223),
        ("PER","Sergio Perez",    "Red Bull Racing", 152),
        ("ALO","Fernando Alonso", "Aston Martin",    162),
        ("TSU","Yuki Tsunoda",    "RB",               30),
        ("HUL","Nico Hulkenberg", "Haas",             31),
        ("STR","Lance Stroll",    "Aston Martin",     24),
        ("GAS","Pierre Gasly",    "Alpine",           42),
        ("OCO","Esteban Ocon",    "Alpine",           23),
        ("ALB","Alexander Albon", "Williams",         12),
    ],
    2023: [
        ("VER","Max Verstappen",   "Red Bull Racing", 575),
        ("PER","Sergio Perez",     "Red Bull Racing", 285),
        ("ALO","Fernando Alonso",  "Aston Martin",    206),
        ("HAM","Lewis Hamilton",   "Mercedes",        234),
        ("LEC","Charles Leclerc", "Ferrari",         206),
        ("SAI","Carlos Sainz",    "Ferrari",         200),
        ("NOR","Lando Norris",     "McLaren",         205),
        ("RUS","George Russell",   "Mercedes",        175),
        ("PIA","Oscar Piastri",    "McLaren",          97),
        ("STR","Lance Stroll",     "Aston Martin",     74),
        ("GAS","Pierre Gasly",     "Alpine",           62),
        ("OCO","Esteban Ocon",     "Alpine",           58),
        ("ALB","Alexander Albon",  "Williams",         27),
        ("BOT","Valtteri Bottas",  "Alfa Romeo",       10),
        ("ZHO","Guanyu Zhou",      "Alfa Romeo",        6),
    ],
    2022: [
        ("VER","Max Verstappen",   "Red Bull Racing", 454),
        ("LEC","Charles Leclerc", "Ferrari",         308),
        ("PER","Sergio Perez",     "Red Bull Racing", 305),
        ("RUS","George Russell",   "Mercedes",        275),
        ("SAI","Carlos Sainz",     "Ferrari",         246),
        ("HAM","Lewis Hamilton",   "Mercedes",        240),
        ("NOR","Lando Norris",     "McLaren",         122),
        ("OCO","Esteban Ocon",     "Alpine",           92),
        ("ALO","Fernando Alonso",  "Alpine",           81),
        ("BOT","Valtteri Bottas",  "Alfa Romeo",       49),
        ("VET","Sebastian Vettel", "Aston Martin",     37),
        ("RIC","Daniel Ricciardo", "McLaren",          19),
        ("STR","Lance Stroll",     "Aston Martin",     18),
        ("TSU","Yuki Tsunoda",     "AlphaTauri",       12),
        ("ZHO","Guanyu Zhou",      "Alfa Romeo",        6),
    ],
    2021: [
        ("VER","Max Verstappen",   "Red Bull Racing", 395),
        ("HAM","Lewis Hamilton",   "Mercedes",        387),
        ("BOT","Valtteri Bottas",  "Mercedes",        226),
        ("PER","Sergio Perez",     "Red Bull Racing", 190),
        ("SAI","Carlos Sainz",     "Ferrari",         164),
        ("NOR","Lando Norris",     "McLaren",         160),
        ("LEC","Charles Leclerc", "Ferrari",         159),
        ("RIC","Daniel Ricciardo", "McLaren",         115),
        ("VET","Sebastian Vettel", "Aston Martin",    100),
        ("ALO","Fernando Alonso",  "Alpine",           81),
        ("OCO","Esteban Ocon",     "Alpine",           74),
        ("STR","Lance Stroll",     "Aston Martin",     34),
        ("GAS","Pierre Gasly",     "AlphaTauri",       110),
        ("ALB","Nicholas Latifi",  "Williams",          7),
        ("TSU","Yuki Tsunoda",     "AlphaTauri",       32),
    ],
    2020: [
        ("HAM","Lewis Hamilton",   "Mercedes",        347),
        ("BOT","Valtteri Bottas",  "Mercedes",        223),
        ("VER","Max Verstappen",   "Red Bull Racing", 214),
        ("PER","Sergio Perez",     "Racing Point",    125),
        ("RIC","Daniel Ricciardo", "Renault",         119),
        ("SAI","Carlos Sainz",     "McLaren",         105),
        ("ALB","Alex Albon",       "Red Bull Racing", 105),
        ("NOR","Lando Norris",     "McLaren",          97),
        ("STR","Lance Stroll",     "Racing Point",     75),
        ("OCO","Esteban Ocon",     "Renault",          62),
        ("GAS","Pierre Gasly",     "AlphaTauri",       75),
        ("VET","Sebastian Vettel", "Ferrari",          33),
        ("LEC","Charles Leclerc", "Ferrari",          98),
        ("RUS","George Russell",   "Williams",          3),
        ("LAT","Nicholas Latifi",  "Williams",          7),
    ],
}

def get_standings(year: int = 2024) -> pd.DataFrame:
    """Retourne le classement championnat pour la saison donnée."""
    data = STANDINGS_BY_YEAR.get(year, STANDINGS_BY_YEAR[2024])
    df = pd.DataFrame(data, columns=["acronym", "name", "team", "points"])
    df = df.sort_values("points", ascending=False).reset_index(drop=True)
    df["position"] = range(1, len(df) + 1)
    df["color"]    = df["acronym"].map(DRIVER_COLORS)
    return df

    return df


def get_session_info(session_key: int) -> dict:
    """Retourne les infos textuelles d'une session (description, conditions)."""
    p = SESSION_PARAMS.get(_safe_int(session_key), SESSION_PARAMS[9473])
    return {
        "desc":         p.get("desc", ""),
        "weather_temp": p.get("weather_temp", 25),
        "track_temp":   p.get("track_temp", 35),
        "wind_speed":   p.get("wind_speed", 10),
        "deg_factor":   p.get("deg_factor", 1.0),
    }
