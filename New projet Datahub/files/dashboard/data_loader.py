"""
data_loader.py — F1 Data Hub · Couche d'abstraction données
════════════════════════════════════════════════════════════
Priorité des sources :
  1. OpenF1 API  — saisons 2023, 2024, 2025 (session_key disponible)
  2. FastF1 API  — saisons 2020, 2021, 2022
  3. mock_data   — fallback si aucune API n'est joignable
"""

import streamlit as st
import pandas as pd
import numpy as np
import os

# ── Mode forcé via variable d'environnement ───────────────────
USE_MOCK_FORCED = os.getenv("USE_MOCK", "false").lower() == "true"

import math as _math

def _safe_key(session_key, default: int = 9473) -> int:
    """Convertit session_key (None, NaN, float, int) en int valide."""
    if session_key is None:
        return default
    try:
        f = float(session_key)
        if _math.isnan(f):
            return default
        return int(f)
    except (TypeError, ValueError):
        return default

# ── Imports mock (toujours disponible) ────────────────────────
from mock_data import (
    get_laps       as _mock_laps,
    get_pit_stops  as _mock_pits,
    get_weather    as _mock_weather,
    get_standings  as _mock_standings,
    get_telemetry  as _mock_telemetry,
    TEAM_COLORS, COMPOUND_COLORS, DRIVER_COLORS,
    DRIVERS_2024, CIRCUIT_COORDS as _MOCK_COORDS,
    hex_to_rgb, hex_to_rgba,
)

from session_catalog import ALL_SESSIONS, CIRCUIT_COORDS

# ── Import optionnel OpenF1 ───────────────────────────────────
try:
    from api_fetcher import (
        get_laps_api      as _api_laps,
        get_pit_stops_api as _api_pits,
        get_weather_api   as _api_weather,
    )
    _OPENF1_IMPORTED = True
except ImportError:
    _OPENF1_IMPORTED = False

# ── Import optionnel FastF1 ───────────────────────────────────
try:
    import fastf1
    _FASTF1_IMPORTED = True
except ImportError:
    _FASTF1_IMPORTED = False


# ════════════════════════════════════════════════════════════════
# Test disponibilité des APIs (cache 60s)
# ════════════════════════════════════════════════════════════════

@st.cache_data(ttl=60, show_spinner=False)
def _openf1_available() -> bool:
    if USE_MOCK_FORCED or not _OPENF1_IMPORTED:
        return False
    try:
        import requests
        r = requests.get("https://api.openf1.org/v1/sessions",
                         params={"session_key": 9473}, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


@st.cache_data(ttl=300, show_spinner=False)
def _fastf1_available() -> bool:
    if USE_MOCK_FORCED or not _FASTF1_IMPORTED:
        return False
    try:
        import fastf1
        return True
    except Exception:
        return False


def _norm_key(session_key):
    """Normalise session_key : NaN/None → None, float → int."""
    import math as _m
    if session_key is None:
        return None
    try:
        f = float(session_key)
        return None if _m.isnan(f) else int(f)
    except (TypeError, ValueError):
        return None



# Mapping circuit name (catalog) → circuit_short_name (OpenF1 API)
_CIRCUIT_TO_OPENF1 = {
    "Sakhir":       "Sakhir",
    "Jeddah":       "Jeddah",
    "Melbourne":    "Melbourne",
    "Shanghai":     "Shanghai",
    "Miami":        "Miami",
    "Imola":        "Imola",
    "Monaco":       "Monaco",
    "Montreal":     "Montréal",
    "Barcelona":    "Barcelona",
    "Spielberg":    "Spielberg",
    "Silverstone":  "Silverstone",
    "Budapest":     "Budapest",
    "Spa":          "Spa-Francorchamps",
    "Zandvoort":    "Zandvoort",
    "Monza":        "Monza",
    "Baku":         "Baku",
    "Singapore":    "Marina Bay",
    "Suzuka":       "Suzuka",
    "Austin":       "Austin",
    "Mexico City":  "Mexico City",
    "Sao Paulo":    "São Paulo",
    "Las Vegas":    "Las Vegas",
    "Lusail":       "Lusail",
    "Abu Dhabi":    "Yas Marina",
    "Portimao":     "Portimão",
    "Istanbul":     "Istanbul",
    "Mugello":      "Mugello",
    "Nurburgring":  "Nürburg",
}

def _resolve_session_key(year: int, round_num: int, circuit: str = None):
    """
    Resout le session_key OpenF1 via meeting_key.
    meetings -> trouver le bon GP -> sessions Race -> session_key.
    Cache 1h.
    """
    if not _openf1_available():
        return None
    try:
        import requests as _req

        # Strategie 1 : recherche par circuit_short_name (plus fiable)
        if circuit and circuit in _CIRCUIT_TO_OPENF1:
            openf1_circuit = _CIRCUIT_TO_OPENF1[circuit]
            r = _req.get("https://api.openf1.org/v1/sessions",
                         params={"year": year, "session_name": "Race",
                                 "circuit_short_name": openf1_circuit},
                         timeout=8)
            if r.status_code == 200 and r.json():
                return int(r.json()[0]["session_key"])

        # Strategie 2 : fallback par numero de manche
        r = _req.get("https://api.openf1.org/v1/meetings",
                     params={"year": year}, timeout=8)
        if r.status_code != 200 or not r.json():
            return None
        meetings = sorted(r.json(), key=lambda m: m.get("date_start", ""))
        gps = [m for m in meetings
               if not any(w in m.get("meeting_name", "")
                          for w in ["Testing", "Test", "Pre-Season"])]
        if round_num > len(gps):
            return None
        meeting_key = gps[round_num - 1]["meeting_key"]
        r2 = _req.get("https://api.openf1.org/v1/sessions",
                      params={"meeting_key": meeting_key, "session_name": "Race"},
                      timeout=8)
        if r2.status_code != 200 or not r2.json():
            return None
        return int(r2.json()[0]["session_key"])
    except Exception:
        return None


# ════════════════════════════════════════════════════════════════
# Catalogue des sessions
# ════════════════════════════════════════════════════════════════

@st.cache_data
def get_sessions(season: int = None) -> pd.DataFrame:
    """
    Retourne le catalogue de sessions.
    Si season est fourni, filtre sur cette saison.
    """
    df = pd.DataFrame(ALL_SESSIONS)
    if season is not None:
        df = df[df["year"] == season].reset_index(drop=True)
    return df


@st.cache_data
def get_available_seasons() -> list:
    return sorted(pd.DataFrame(ALL_SESSIONS)["year"].unique().tolist(), reverse=True)


# ════════════════════════════════════════════════════════════════
# FastF1 — chargement données réelles 2020-2022
# ════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Chargement FastF1...", ttl=3600)
def _load_fastf1_laps(year: int, round_num: int) -> pd.DataFrame:
    """Charge les données de tours via FastF1."""
    try:
        import fastf1
        fastf1.Cache.enable_cache("f1_cache")
        session = fastf1.get_session(year, round_num, "R")
        session.load(laps=True, telemetry=False, weather=False)
        laps = session.laps

        df = pd.DataFrame({
            "driver":       laps["Driver"],
            "lap_number":   laps["LapNumber"].astype(int),
            "lap_time_s":   laps["LapTime"].dt.total_seconds(),
            "sector1_s":    laps["Sector1Time"].dt.total_seconds(),
            "sector2_s":    laps["Sector2Time"].dt.total_seconds(),
            "sector3_s":    laps["Sector3Time"].dt.total_seconds(),
            "compound":     laps["Compound"].fillna("UNKNOWN"),
            "tyre_life":    laps["TyreLife"].fillna(0).astype(int),
            "speed_fl_kmh": laps["SpeedFL"].fillna(0),
            "team":         laps["Team"],
        })
        df = df.dropna(subset=["lap_time_s"])
        df["is_personal_best"] = df.groupby("driver")["lap_time_s"].transform(
            lambda x: x == x.cummin()
        )
        # Ajouter les couleurs depuis DRIVER_COLORS
        df["color"] = df["driver"].map(DRIVER_COLORS).fillna("rgb(128,128,128)")
        return df
    except Exception as e:
        st.warning(f"FastF1 indisponible : {e}. Utilisation des données simulées.")
        return pd.DataFrame()


def _load_fastf1_weather(year: int, round_num: int) -> pd.DataFrame:
    """FastF1 weather désactivé — NameError interne irrécupérable."""
    return pd.DataFrame()


# ════════════════════════════════════════════════════════════════
# Fonctions publiques
# ════════════════════════════════════════════════════════════════

def _get_session_meta(session_key: int) -> dict:
    """Retrouve les métadonnées d'une session depuis le catalogue."""
    df = pd.DataFrame(ALL_SESSIONS)
    row = df[df["session_key"] == session_key]
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


REQUIRED_LAP_COLS = [
    "driver", "team", "lap_number", "lap_time_s",
    "sector1_s", "sector2_s", "sector3_s",
    "compound", "tyre_life", "is_personal_best",
]

def _ensure_lap_cols(df: pd.DataFrame, session_key: int, n_laps: int) -> pd.DataFrame:
    """Garantit que le DataFrame a toutes les colonnes requises. Fallback mock si non."""
    if df.empty or not all(c in df.columns for c in REQUIRED_LAP_COLS):
        return _mock_laps(_safe_key(session_key), n_laps)
    return df


@st.cache_data(ttl=60, show_spinner=False)
def get_laps(session_key=None, n_laps: int = 57,
             year: int = 2024, round_num: int = 1, circuit: str = None) -> pd.DataFrame:
    """Retourne les tours — OpenF1 (2023+) → FastF1 (2020-2022) → mock."""
    session_key = _norm_key(session_key)
    _sk = _safe_key(session_key)

    if session_key is None and year >= 2023:
        resolved = _resolve_session_key(year, round_num, circuit)
        if resolved:
            session_key = resolved
            _sk = resolved

    # ── OpenF1 (2023+) ────────────────────────────────────────
    if year >= 2023 and session_key and _openf1_available():
        try:
            df = _api_laps(session_key)
            if not df.empty:
                return _ensure_lap_cols(df, _sk, n_laps)
        except Exception:
            pass

    # ── FastF1 (2020-2022) ────────────────────────────────────
    if year <= 2022 and _fastf1_available():
        df = _load_fastf1_laps(year, round_num)
        if not df.empty:
            df["session_key"] = session_key
            return _ensure_lap_cols(df, _sk, n_laps)

    # ── Mock (fallback garanti) ───────────────────────────────
    return _mock_laps(_sk, n_laps, year=year, round_num=round_num)


REQUIRED_PIT_COLS = ["driver", "lap_number", "pit_duration_s"]

def _ensure_pit_cols(df: pd.DataFrame, session_key) -> pd.DataFrame:
    """Garantit que df_pit a les colonnes requises, sinon retourne le mock."""
    if df.empty or not all(c in df.columns for c in REQUIRED_PIT_COLS):
        return _mock_pits(_safe_key(session_key), year=year, round_num=round_num)
    return df


@st.cache_data(ttl=60, show_spinner=False)
def get_pit_stops(session_key=None, year: int = 2024,
                  round_num: int = 1, circuit: str = None) -> pd.DataFrame:
    session_key = _norm_key(session_key)
    _sk = _safe_key(session_key)
    if session_key is None and year >= 2023:
        session_key = _resolve_session_key(year, round_num, circuit)
    if year >= 2023 and session_key and _openf1_available():
        try:
            df = _api_pits(session_key)
            return _ensure_pit_cols(df, _sk)
        except Exception:
            pass
    return _mock_pits(_sk)


@st.cache_data(ttl=60, show_spinner=False)
def get_weather(session_key=None, n_points: int = 57,
                year: int = 2024, round_num: int = 1, circuit: str = None) -> pd.DataFrame:
    import math as _m
    # Normaliser session_key — NaN et None traitĂ©s comme None
    if session_key is not None:
        try:
            if _m.isnan(float(session_key)):
                session_key = None
            else:
                session_key = int(float(session_key))
        except (TypeError, ValueError):
            session_key = None

    _sk = _safe_key(session_key)

    # Résolution dynamique uniquement pour 2023+
    if session_key is None and year >= 2023:
        session_key = _resolve_session_key(year, round_num, circuit)

    if year >= 2023 and session_key and _openf1_available():
        try:
            df = _api_weather(session_key)
            if not df.empty and "air_temperature" in df.columns:
                return df
        except Exception:
            pass

    if year <= 2022 and _fastf1_available():
        try:
            df = _load_fastf1_weather(year, round_num)
            if not df.empty and "air_temperature" in df.columns:
                return df
        except Exception:
            pass

    return _mock_weather(_sk, n_points, year=year, round_num=round_num)


def get_standings(year: int = 2024) -> pd.DataFrame:
    """Retourne le classement championnat pour l'année donnée."""
    df = _mock_standings()
    # Adapter les points selon l'année (simulation réaliste)
    if not df.empty and year != 2024:
        import numpy as np
        np.random.seed(year)
        df = df.copy()
        df["points"] = np.random.randint(50, 600, size=len(df))
        df = df.sort_values("points", ascending=False).reset_index(drop=True)
    return df


def get_telemetry(driver: str, laps: int = 50,
                   year: int = 2024, round_num: int = 1) -> pd.DataFrame:
    return _mock_telemetry(driver, laps, year=year, round_num=round_num)


def get_source_label(session_key=None, year: int = 2024) -> str:
    """Retourne le label de la source de données active."""
    if year >= 2023 and session_key and _openf1_available():
        return "🟢 OpenF1 API — données réelles"
    if year <= 2022 and _fastf1_available():
        return "🔵 FastF1 — données réelles"
    return "🟡 Simulation — données générées"


def show_source_badge(session_key=None, year: int = 2024):
    label = get_source_label(session_key, year)
    color = {"🟢": "#1D9E75", "🔵": "#185FA5", "🟡": "#BA7517"}.get(label[0], "#888")
    st.markdown(
        f'<div style="font-size:11px;color:{color};margin-bottom:8px">{label}</div>',
        unsafe_allow_html=True,
    )
