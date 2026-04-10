# ═══════════════════════════════════════════════════════════════
# etl/extractors/jolpica_extractor.py
# Source historique F1 — successeur open source de l'API Ergast
# ═══════════════════════════════════════════════════════════════

import requests
import logging
from typing import List, Dict, Tuple, Optional

log = logging.getLogger(__name__)
BASE_URL = "https://api.jolpi.ca/ergast/f1"
TIMEOUT  = 15


def _get(path: str) -> dict:
    try:
        r = requests.get(f"{BASE_URL}/{path}.json", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json().get("MRData", {})
    except Exception as e:
        log.error(f"Jolpica error : {e}")
        return {}


def extract_jolpica_sessions(year: int) -> List[Dict]:
    """Retourne le calendrier des courses d'une saison."""
    data = _get(f"{year}")
    races = data.get("RaceTable", {}).get("Races", [])
    sessions = []
    for race in races:
        sessions.append({
            "session_key": None,
            "year":        year,
            "round":       int(race["round"]),
            "gp_name":     race.get("raceName", ""),
            "circuit":     race.get("Circuit", {}).get("circuitName", ""),
            "country":     race.get("Circuit", {}).get("Location", {}).get("country", ""),
            "date_start":  race.get("date"),
            "session_type": "Race",
            "source":      "jolpica",
        })
    log.info(f"Jolpica : {len(sessions)} courses — saison {year}")
    return sessions


def extract_jolpica_standings(
    year: int, round_num: Optional[int] = None
) -> Tuple[List[Dict], List[Dict]]:
    """Retourne les classements pilotes et équipes."""
    path_suffix = f"{year}" if round_num is None else f"{year}/{round_num}"

    # Classement pilotes
    data_d   = _get(f"{path_suffix}/driverstandings")
    standings = data_d.get("StandingsTable", {}).get("StandingsLists", [])
    round_val = round_num or (standings[0].get("round", 0) if standings else 0)

    driver_rows = []
    if standings:
        for entry in standings[0].get("DriverStandings", []):
            driver_rows.append({
                "year":       year,
                "round":      int(round_val),
                "driver_id":  entry["Driver"]["driverId"],
                "full_name":  f"{entry['Driver']['givenName']} {entry['Driver']['familyName']}",
                "team_name":  entry["Constructors"][0]["name"] if entry.get("Constructors") else "",
                "position":   int(entry.get("position", 0)),
                "points":     float(entry.get("points", 0)),
                "wins":       int(entry.get("wins", 0)),
            })

    # Classement équipes
    data_t    = _get(f"{path_suffix}/constructorstandings")
    standings_t = data_t.get("StandingsTable", {}).get("StandingsLists", [])

    team_rows = []
    if standings_t:
        for entry in standings_t[0].get("ConstructorStandings", []):
            team_rows.append({
                "year":      year,
                "round":     int(round_val),
                "team_id":   entry["Constructor"]["constructorId"],
                "team_name": entry["Constructor"]["name"],
                "position":  int(entry.get("position", 0)),
                "points":    float(entry.get("points", 0)),
                "wins":      int(entry.get("wins", 0)),
            })

    log.info(f"Jolpica standings : {len(driver_rows)} pilotes, {len(team_rows)} équipes — {year}")
    return driver_rows, team_rows


def extract_jolpica_results(year: int, round_num: int) -> List[Dict]:
    """Résultats détaillés d'une course."""
    data  = _get(f"{year}/{round_num}/results")
    races = data.get("RaceTable", {}).get("Races", [])
    if not races:
        return []

    rows = []
    for result in races[0].get("Results", []):
        rows.append({
            "year":           year,
            "round":          round_num,
            "driver_id":      result["Driver"]["driverId"],
            "full_name":      f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
            "team_name":      result.get("Constructor", {}).get("name", ""),
            "position":       int(result.get("position", 0)) if result.get("position", "").isdigit() else None,
            "points":         float(result.get("points", 0)),
            "grid_position":  int(result.get("grid", 0)),
            "status":         result.get("status", ""),
            "fastest_lap":    result.get("FastestLap", {}).get("rank") == "1",
        })
    return rows


# ═══════════════════════════════════════════════════════════════