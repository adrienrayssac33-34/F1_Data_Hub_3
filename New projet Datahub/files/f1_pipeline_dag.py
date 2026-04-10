# ═══════════════════════════════════════════════════════════════
# airflow/dags/f1_pipeline_dag.py
# DAG principal du pipeline F1 Data Hub
# Ordonnancement : quotidien · idempotent · fault-tolerant
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations
import os
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

log = logging.getLogger(__name__)

# ── Paramètres par défaut ────────────────────────────────────
DEFAULT_ARGS = {
    "owner":            "f1_team",
    "depends_on_past":  False,
    "email_on_failure": False,
    "email_on_retry":   False,
    "retries":          2,
    "retry_delay":      timedelta(minutes=5),
}

# ── Import des extracteurs ETL ────────────────────────────────
import sys
sys.path.insert(0, "/opt/airflow/etl")

from extractors.openf1_extractor  import extract_openf1_session
from extractors.fastf1_extractor  import extract_fastf1_session
from extractors.jolpica_extractor import extract_jolpica_standings
from loaders.postgres_loader      import load_to_postgres, upsert_sessions


# ════════════════════════════════════════════════════════════════
# Fonctions des tâches
# ════════════════════════════════════════════════════════════════

def task_extract_sessions(**context):
    """Récupère le catalogue des sessions de la saison courante via Jolpica."""
    from extractors.jolpica_extractor import extract_jolpica_sessions
    year = context["params"].get("year", datetime.now().year)
    sessions = extract_jolpica_sessions(year)
    log.info(f"Sessions extraites : {len(sessions)} pour {year}")
    context["ti"].xcom_push(key="sessions", value=sessions)


def task_extract_laps(**context):
    """Extrait les tours de la dernière course via OpenF1 ou FastF1."""
    sessions = context["ti"].xcom_pull(key="sessions", task_ids="extract_sessions")
    if not sessions:
        log.warning("Aucune session à traiter")
        return

    year = context["params"].get("year", datetime.now().year)

    for session in sessions:
        session_key = session.get("session_key")
        round_num   = session.get("round")

        if session_key and year >= 2023:
            log.info(f"Extraction OpenF1 — session_key={session_key}")
            laps = extract_openf1_session(session_key)
        else:
            log.info(f"Extraction FastF1 — {year} R{round_num:02d}")
            laps = extract_fastf1_session(year, round_num)

        if laps:
            load_to_postgres(laps, table="raw.laps", conflict_cols=["session_key","driver_number","lap_number"])
            log.info(f"Chargé {len(laps)} tours — session_key={session_key}")


def task_extract_standings(**context):
    """Extrait les classements pilotes et équipes via Jolpica."""
    year      = context["params"].get("year", datetime.now().year)
    round_num = context["params"].get("round", None)

    driver_standings, team_standings = extract_jolpica_standings(year, round_num)

    load_to_postgres(driver_standings, table="raw.driver_standings",
                     conflict_cols=["year","round","driver_id"])
    load_to_postgres(team_standings,   table="raw.team_standings",
                     conflict_cols=["year","round","team_id"])

    log.info(f"Classements chargés — {len(driver_standings)} pilotes, {len(team_standings)} équipes")


def task_extract_weather(**context):
    """Extrait la météo via OpenF1 pour les sessions 2023+."""
    from extractors.openf1_extractor import extract_openf1_weather
    sessions = context["ti"].xcom_pull(key="sessions", task_ids="extract_sessions")
    if not sessions:
        return

    for session in sessions:
        session_key = session.get("session_key")
        if not session_key:
            continue
        weather = extract_openf1_weather(session_key)
        if weather:
            load_to_postgres(weather, table="raw.weather",
                             conflict_cols=["session_key","measurement_time"])
            log.info(f"Météo chargée — {len(weather)} points — session_key={session_key}")


def task_quality_check(**context):
    """Contrôle qualité basique — vérifie les tables raw non vides."""
    import psycopg2
    conn_str = os.getenv("F1_DB_CONN", "postgresql://f1user:f1pass@postgres/f1_data_hub")

    checks = [
        ("raw.sessions",       "SELECT COUNT(*) FROM raw.sessions"),
        ("raw.laps",           "SELECT COUNT(*) FROM raw.laps"),
        ("raw.driver_standings","SELECT COUNT(*) FROM raw.driver_standings"),
    ]

    conn = psycopg2.connect(conn_str)
    cur  = conn.cursor()
    passed = True

    for table, query in checks:
        cur.execute(query)
        count = cur.fetchone()[0]
        if count == 0:
            log.warning(f"QUALITY CHECK FAILED : {table} est vide")
            passed = False
        else:
            log.info(f"QUALITY CHECK OK : {table} — {count} lignes")

    cur.close()
    conn.close()

    if not passed:
        raise ValueError("Quality checks échoués — pipeline interrompu avant dbt")


# ════════════════════════════════════════════════════════════════
# DAG
# ════════════════════════════════════════════════════════════════

with DAG(
    dag_id="f1_pipeline",
    description="Pipeline ETL complet F1 Data Hub — extraction, chargement, transformation dbt",
    default_args=DEFAULT_ARGS,
    schedule_interval="0 8 * * *",   # Tous les jours à 8h UTC
    start_date=days_ago(1),
    catchup=False,
    tags=["f1", "etl", "production"],
    params={
        "year":  datetime.now().year,
        "round": None,
    },
    doc_md="""
    ## F1 Data Hub — Pipeline principal

    **Étapes :**
    1. `extract_sessions`   — catalogue des sessions (Jolpica)
    2. `extract_laps`       — tours par session (OpenF1 ou FastF1)
    3. `extract_standings`  — classements pilotes + équipes (Jolpica)
    4. `extract_weather`    — météo (OpenF1 2023+)
    5. `quality_check`      — contrôle tables raw non vides
    6. `dbt_run`            — transformation staging + mart
    7. `dbt_test`           — tests de qualité dbt

    **Sources :**
    - OpenF1 API  : sessions 2023–2025
    - FastF1      : sessions 2020–2022 (cache local)
    - Jolpica     : classements et résultats historiques
    """,
) as dag:

    t_extract_sessions = PythonOperator(
        task_id="extract_sessions",
        python_callable=task_extract_sessions,
    )

    t_extract_laps = PythonOperator(
        task_id="extract_laps",
        python_callable=task_extract_laps,
    )

    t_extract_standings = PythonOperator(
        task_id="extract_standings",
        python_callable=task_extract_standings,
    )

    t_extract_weather = PythonOperator(
        task_id="extract_weather",
        python_callable=task_extract_weather,
    )

    t_quality_check = PythonOperator(
        task_id="quality_check",
        python_callable=task_quality_check,
    )

    t_dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /dbt && dbt run --profiles-dir /dbt",
    )

    t_dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /dbt && dbt test --profiles-dir /dbt",
    )

    # ── Dépendances ───────────────────────────────────────────
    t_extract_sessions >> [t_extract_laps, t_extract_standings, t_extract_weather]
    [t_extract_laps, t_extract_standings, t_extract_weather] >> t_quality_check
    t_quality_check >> t_dbt_run >> t_dbt_test
