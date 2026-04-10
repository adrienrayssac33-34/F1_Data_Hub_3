import os
import psycopg2
import psycopg2.extras
import logging
from typing import List, Dict

log = logging.getLogger(__name__)


def _get_conn():
    conn_str = os.getenv("F1_DB_CONN", "postgresql://f1user:f1pass@postgres/f1_data_hub")
    return psycopg2.connect(conn_str)


def load_to_postgres(
    rows: List[Dict],
    table: str,
    conflict_cols: List[str] = None,
) -> int:
    """
    Charge une liste de dicts dans une table PostgreSQL.
    Idempotent : ON CONFLICT DO NOTHING sur conflict_cols.
    Retourne le nombre de lignes insérées.
    """
    if not rows:
        log.info(f"load_to_postgres : rien à charger pour {table}")
        return 0

    cols    = list(rows[0].keys())
    placeholders = ",".join(["%s"] * len(cols))
    col_names    = ",".join(cols)

    conflict_clause = ""
    if conflict_cols:
        conflict_clause = f"ON CONFLICT ({','.join(conflict_cols)}) DO NOTHING"

    sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) {conflict_clause}"

    try:
        conn = _get_conn()
        cur  = conn.cursor()
        data = [[row.get(c) for c in cols] for row in rows]
        psycopg2.extras.execute_batch(cur, sql, data, page_size=500)
        inserted = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        log.info(f"load_to_postgres : {inserted} lignes → {table}")
        return inserted
    except Exception as e:
        log.error(f"load_to_postgres erreur : {e}")
        raise


def upsert_sessions(sessions: List[Dict]) -> int:
    """
    Upsert spécifique pour raw.sessions avec mise à jour du session_key OpenF1.
    """
    if not sessions:
        return 0

    sql = """
        INSERT INTO raw.sessions
            (session_key, year, round, gp_name, circuit, country, date_start,
             session_type, track_km, total_laps, source)
        VALUES
            (%(session_key)s, %(year)s, %(round)s, %(gp_name)s, %(circuit)s,
             %(country)s, %(date_start)s, %(session_type)s, %(track_km)s,
             %(total_laps)s, %(source)s)
        ON CONFLICT (session_key) DO UPDATE SET
            session_key = EXCLUDED.session_key,
            gp_name     = EXCLUDED.gp_name,
            circuit     = EXCLUDED.circuit,
            source      = EXCLUDED.source
        WHERE raw.sessions.session_key = EXCLUDED.session_key
    """

    try:
        conn = _get_conn()
        cur  = conn.cursor()
        psycopg2.extras.execute_batch(cur, sql, sessions, page_size=100)
        conn.commit()
        cur.close()
        conn.close()
        log.info(f"upsert_sessions : {len(sessions)} sessions chargées")
        return len(sessions)
    except Exception as e:
        log.error(f"upsert_sessions erreur : {e}")
        raise