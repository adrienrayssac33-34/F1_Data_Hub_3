# ═══════════════════════════════════════════════════════════════
# etl/extractors/fastf1_extractor.py
# ═══════════════════════════════════════════════════════════════

import logging
import math
import numpy as np
from typing import List, Dict

log = logging.getLogger(__name__)
CACHE_DIR = "/opt/airflow/fastf1_cache"


def extract_fastf1_session(year: int, round_num: int) -> List[Dict]:
    """
    Extrait les tours d'une session via FastF1 (2020–2022).
    Cache activé dans CACHE_DIR pour éviter les re-téléchargements.
    """
    try:
        import fastf1
        fastf1.Cache.enable_cache(CACHE_DIR)

        session = fastf1.get_session(year, round_num, "R")
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        laps = session.laps.copy()

        if laps.empty:
            log.warning(f"FastF1 : aucun tour — {year} R{round_num:02d}")
            return []

        def td_to_s(td):
            try:
                return round(td.total_seconds(), 3)
            except Exception:
                return None

        rows = []
        for _, row in laps.iterrows():
            lap_s = td_to_s(row.get("LapTime"))
            if lap_s is None or math.isnan(lap_s):
                continue
            rows.append({
                "session_key":     None,   # FastF1 n'a pas de session_key OpenF1
                "driver_number":   None,
                "acronym":         str(row.get("Driver", "")),
                "lap_number":      int(row.get("LapNumber", 0)),
                "lap_time_s":      lap_s,
                "sector1_s":       td_to_s(row.get("Sector1Time")),
                "sector2_s":       td_to_s(row.get("Sector2Time")),
                "sector3_s":       td_to_s(row.get("Sector3Time")),
                "compound":        str(row.get("Compound", "UNKNOWN")),
                "tyre_life":       int(row.get("TyreLife", 0)) if row.get("TyreLife") else None,
                "speed_fl_kmh":    float(row.get("SpeedFL", 0)) if row.get("SpeedFL") else None,
                "is_personal_best": False,
            })

        log.info(f"FastF1 : {len(rows)} tours extraits — {year} R{round_num:02d}")
        return rows

    except ImportError:
        log.error("fastf1 non installé — pip install fastf1")
        return []
    except Exception as e:
        log.error(f"FastF1 erreur : {e}")
        return []
