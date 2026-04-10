# ═══════════════════════════════════════════════════════════════
# etl/extractors/openf1_extractor.py
# ═══════════════════════════════════════════════════════════════

import requests
import logging
from typing import List, Dict, Optional

log = logging.getLogger(__name__)
BASE_URL = "https://api.openf1.org/v1"
TIMEOUT  = 15


def _get(endpoint: str, params: dict) -> list:
    """Appel GET OpenF1 avec gestion d'erreurs silencieuse."""
    clean = {k: int(float(v)) if isinstance(v, float) else v
             for k, v in params.items()}
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", params=clean, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        if "404" in str(e):
            log.warning(f"OpenF1 404 — {endpoint} {clean}")
            return []
        log.error(f"OpenF1 HTTP error : {e}")
        return []
    except Exception as e:
        log.error(f"OpenF1 error : {e}")
        return []


def extract_openf1_session(session_key: int) -> List[Dict]:
    """Extrait tous les tours d'une session OpenF1."""
    data = _get("laps", {"session_key": session_key})
    if not data:
        return []

    rows = []
    for d in data:
        rows.append({
            "session_key":     session_key,
            "driver_number":   d.get("driver_number"),
            "lap_number":      d.get("lap_number"),
            "lap_time_s":      d.get("lap_duration"),
            "sector1_s":       d.get("duration_sector_1"),
            "sector2_s":       d.get("duration_sector_2"),
            "sector3_s":       d.get("duration_sector_3"),
            "compound":        d.get("compound", "UNKNOWN"),
            "tyre_life":       d.get("tyre_life_laps"),
            "speed_fl_kmh":    d.get("st_speed"),
            "is_personal_best": d.get("is_pit_out_lap", False) is False,
        })
    log.info(f"OpenF1 : {len(rows)} tours extraits — session_key={session_key}")
    return rows


def extract_openf1_weather(session_key: int) -> List[Dict]:
    """Extrait les données météo d'une session OpenF1."""
    data = _get("weather", {"session_key": session_key})
    rows = []
    for d in data:
        rows.append({
            "session_key":        session_key,
            "measurement_time":   d.get("date"),
            "air_temperature":    d.get("air_temperature"),
            "track_temperature":  d.get("track_temperature"),
            "humidity":           d.get("humidity"),
            "wind_speed":         d.get("wind_speed"),
            "wind_direction":     d.get("wind_direction"),
            "rainfall":           d.get("rainfall", 0),
        })
    return rows


def extract_openf1_pit_stops(session_key: int) -> List[Dict]:
    """Extrait les pit stops d'une session OpenF1."""
    data = _get("pit", {"session_key": session_key})
    rows = []
    for d in data:
        rows.append({
            "session_key":    session_key,
            "driver_number":  d.get("driver_number"),
            "lap_number":     d.get("lap_number"),
            "pit_duration_s": d.get("pit_duration"),
        })
    return rows


def resolve_session_key(year: int, round_num: int, circuit: str = None) -> Optional[int]:
    """
    Résout le session_key OpenF1 par circuit_short_name ou par meeting.
    Retourne None si introuvable.
    """
    CIRCUIT_MAP = {
        "Sakhir": "Sakhir", "Jeddah": "Jeddah", "Melbourne": "Melbourne",
        "Shanghai": "Shanghai", "Miami": "Miami", "Imola": "Imola",
        "Monaco": "Monaco", "Montreal": "Montréal", "Barcelona": "Barcelona",
        "Spielberg": "Spielberg", "Silverstone": "Silverstone", "Budapest": "Budapest",
        "Spa": "Spa-Francorchamps", "Zandvoort": "Zandvoort", "Monza": "Monza",
        "Baku": "Baku", "Singapore": "Marina Bay", "Suzuka": "Suzuka",
        "Austin": "Austin", "Mexico City": "Mexico City", "Sao Paulo": "São Paulo",
        "Las Vegas": "Las Vegas", "Lusail": "Lusail", "Abu Dhabi": "Yas Marina",
    }

    # Stratégie 1 : par circuit
    if circuit and circuit in CIRCUIT_MAP:
        data = _get("sessions", {
            "year": year,
            "session_name": "Race",
            "circuit_short_name": CIRCUIT_MAP[circuit],
        })
        if data:
            return int(data[0]["session_key"])

    # Stratégie 2 : par numéro de manche
    meetings = _get("meetings", {"year": year})
    if not meetings:
        return None
    meetings = sorted(meetings, key=lambda m: m.get("date_start", ""))
    gps = [m for m in meetings if not any(
        w in m.get("meeting_name", "") for w in ["Testing", "Test"]
    )]
    if round_num > len(gps):
        return None
    meeting_key = gps[round_num - 1]["meeting_key"]
    data = _get("sessions", {"meeting_key": meeting_key, "session_name": "Race"})
    return int(data[0]["session_key"]) if data else None
