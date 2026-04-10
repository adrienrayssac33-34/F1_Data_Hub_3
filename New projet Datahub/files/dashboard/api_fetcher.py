"""
api_fetcher.py — F1 Data Hub · Connecteur OpenF1 API
═══════════════════════════════════════════════════════
Pour passer en production : remplacer les appels mock_data.get_*()
par les fonctions ci-dessous dans chaque page.

Documentation OpenF1 : https://openf1.org/
Endpoints utilisés   : /v1/laps · /v1/pit · /v1/weather · /v1/sessions

Usage :
    from api_fetcher import get_laps_api, get_pit_stops_api, get_weather_api
    df = get_laps_api(session_key=9473)
"""

import requests
import pandas as pd
import streamlit as st

BASE_URL = "https://api.openf1.org/v1"
TIMEOUT  = 15  # secondes


def _fetch(endpoint: str, params: dict) -> list:
    """Appel générique à l'API OpenF1. Force les clés numériques en int."""
    clean_params = {}
    for k, v in params.items():
        try:
            clean_params[k] = int(float(v))
        except (TypeError, ValueError):
            clean_params[k] = v
    try:
        resp = requests.get(f"{BASE_URL}/{endpoint}", params=clean_params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return []
    except requests.exceptions.Timeout:
        return []
    except requests.exceptions.HTTPError as e:
        err = str(e)
        if "404" in err:
            return []  # Session non trouvée — fallback silencieux
        if "429" in err:
            return []  # Rate limit — fallback silencieux vers mock
        st.warning(f"⚠️ API OpenF1 : {e}")
        return []


@st.cache_data(ttl=300, show_spinner="Chargement des tours depuis OpenF1...")
def get_laps_api(session_key: int) -> pd.DataFrame:
    """
    Récupère les données de tours depuis OpenF1.
    TTL 5 min — données mises en cache pour éviter les appels répétés.
    """
    data = _fetch("laps", {"session_key": session_key})
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    # Normalisation des colonnes pour compatibilité avec les pages
    rename = {
        "driver_number":    "driver_number",
        "lap_number":       "lap_number",
        "lap_duration":     "lap_time_s",
        "duration_sector_1": "sector1_s",
        "duration_sector_2": "sector2_s",
        "duration_sector_3": "sector3_s",
        "compound":         "compound",
        "tyre_life_laps":   "tyre_life",
        "st_speed":         "speed_fl_kmh",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    # Convertir les types
    for col in ["lap_time_s", "sector1_s", "sector2_s", "sector3_s"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["session_key"] = session_key
    return df


@st.cache_data(ttl=300, show_spinner="Chargement des pit stops depuis OpenF1...")
def get_pit_stops_api(session_key: int) -> pd.DataFrame:
    """Récupère les pit stops depuis OpenF1."""
    data = _fetch("pit", {"session_key": session_key})
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    rename = {
        "lap_number":    "lap_number",
        "pit_duration":  "pit_duration_s",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    df["session_key"] = session_key
    return df


@st.cache_data(ttl=300, show_spinner="Chargement de la météo depuis OpenF1...")
def get_weather_api(session_key: int) -> pd.DataFrame:
    """Récupère les données météo depuis OpenF1."""
    data = _fetch("weather", {"session_key": session_key})
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    rename = {
        "date":               "date",
        "air_temperature":    "air_temperature",
        "track_temperature":  "track_temperature",
        "humidity":           "humidity",
        "wind_speed":         "wind_speed",
        "wind_direction":     "wind_direction",
        "rainfall":           "rainfall",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["session_key"] = session_key
    return df


@st.cache_data(ttl=3600)
def get_sessions_api(year: int = 2024) -> pd.DataFrame:
    """
    Récupère la liste des sessions depuis OpenF1.
    TTL 1h — les sessions ne changent pas souvent.
    """
    data = _fetch("sessions", {"year": year, "session_name": "Race"})
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    rename = {
        "session_key":    "session_key",
        "meeting_name":   "gp_name",
        "circuit_short_name": "circuit",
        "country_code":   "country",
        "date_start":     "date",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


# ── Instructions de migration ────────────────────────────────────
MIGRATION_GUIDE = """
PASSAGE EN PRODUCTION — MODE D'EMPLOI
═══════════════════════════════════════
Dans chaque fichier pages/*.py, remplacer :

    from mock_data import get_laps, get_pit_stops, get_weather
    df = get_laps(session_key, n_laps)

Par :

    from api_fetcher import get_laps_api, get_pit_stops_api, get_weather_api
    df = get_laps_api(session_key)

Les colonnes sont normalisées pour rester compatibles.
Aucune autre modification des pages n'est nécessaire.
"""
