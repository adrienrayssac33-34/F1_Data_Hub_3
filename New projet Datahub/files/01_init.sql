-- ═══════════════════════════════════════════════════════════════
-- F1 Data Hub — PostgreSQL initialisation
-- Crée la base, l'utilisateur, les schémas raw/staging/mart
-- Exécuté automatiquement au premier démarrage du conteneur
-- ═══════════════════════════════════════════════════════════════

-- Base de données F1
CREATE DATABASE f1_data_hub;

-- Utilisateur applicatif
CREATE USER f1user WITH PASSWORD 'f1pass';
GRANT ALL PRIVILEGES ON DATABASE f1_data_hub TO f1user;

-- Base Airflow (si pas déjà créée)
CREATE DATABASE airflow;
CREATE USER airflow WITH PASSWORD 'airflow';
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

\connect f1_data_hub

-- Schémas (couches dbt)
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;

GRANT ALL ON SCHEMA raw     TO f1user;
GRANT ALL ON SCHEMA staging TO f1user;
GRANT ALL ON SCHEMA mart    TO f1user;

-- ── Tables RAW ──────────────────────────────────────────────
-- Sessions
CREATE TABLE IF NOT EXISTS raw.sessions (
    session_key     INTEGER PRIMARY KEY,
    year            INTEGER NOT NULL,
    round           INTEGER NOT NULL,
    gp_name         TEXT    NOT NULL,
    circuit         TEXT    NOT NULL,
    country         TEXT,
    date_start      TIMESTAMP,
    session_type    TEXT    DEFAULT 'Race',
    track_km        NUMERIC(5,3),
    total_laps      INTEGER,
    source          TEXT,        -- 'openf1' | 'fastf1' | 'jolpica'
    loaded_at       TIMESTAMP   DEFAULT NOW()
);

-- Pilotes
CREATE TABLE IF NOT EXISTS raw.drivers (
    driver_id       SERIAL PRIMARY KEY,
    session_key     INTEGER REFERENCES raw.sessions(session_key),
    acronym         TEXT    NOT NULL,
    full_name       TEXT,
    team_name       TEXT,
    team_color      TEXT,
    driver_number   INTEGER,
    country_code    TEXT,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

-- Tours
CREATE TABLE IF NOT EXISTS raw.laps (
    id              BIGSERIAL PRIMARY KEY,
    session_key     INTEGER REFERENCES raw.sessions(session_key),
    driver_number   INTEGER,
    acronym         TEXT,
    lap_number      INTEGER,
    lap_time_s      NUMERIC(8,3),
    sector1_s       NUMERIC(7,3),
    sector2_s       NUMERIC(7,3),
    sector3_s       NUMERIC(7,3),
    compound        TEXT,
    tyre_life       INTEGER,
    speed_fl_kmh    NUMERIC(6,1),
    is_personal_best BOOLEAN,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

-- Pit stops
CREATE TABLE IF NOT EXISTS raw.pit_stops (
    id              BIGSERIAL PRIMARY KEY,
    session_key     INTEGER REFERENCES raw.sessions(session_key),
    driver_number   INTEGER,
    acronym         TEXT,
    lap_number      INTEGER,
    pit_duration_s  NUMERIC(6,2),
    loaded_at       TIMESTAMP DEFAULT NOW()
);

-- Météo
CREATE TABLE IF NOT EXISTS raw.weather (
    id              BIGSERIAL PRIMARY KEY,
    session_key     INTEGER REFERENCES raw.sessions(session_key),
    measurement_time TIMESTAMP,
    air_temperature NUMERIC(5,1),
    track_temperature NUMERIC(5,1),
    humidity        NUMERIC(5,1),
    wind_speed      NUMERIC(5,1),
    wind_direction  INTEGER,
    rainfall        NUMERIC(5,1),
    loaded_at       TIMESTAMP DEFAULT NOW()
);

-- Résultats course (Jolpica)
CREATE TABLE IF NOT EXISTS raw.race_results (
    id              BIGSERIAL PRIMARY KEY,
    session_key     INTEGER,
    year            INTEGER,
    round           INTEGER,
    driver_id       TEXT,
    full_name       TEXT,
    team_name       TEXT,
    position        INTEGER,
    points          NUMERIC(5,1),
    grid_position   INTEGER,
    status          TEXT,
    fastest_lap     BOOLEAN,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

-- Standings pilotes (Jolpica)
CREATE TABLE IF NOT EXISTS raw.driver_standings (
    id              BIGSERIAL PRIMARY KEY,
    year            INTEGER,
    round           INTEGER,
    driver_id       TEXT,
    full_name       TEXT,
    team_name       TEXT,
    position        INTEGER,
    points          NUMERIC(6,1),
    wins            INTEGER,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

-- Standings équipes (Jolpica)
CREATE TABLE IF NOT EXISTS raw.team_standings (
    id              BIGSERIAL PRIMARY KEY,
    year            INTEGER,
    round           INTEGER,
    team_id         TEXT,
    team_name       TEXT,
    position        INTEGER,
    points          NUMERIC(6,1),
    wins            INTEGER,
    loaded_at       TIMESTAMP DEFAULT NOW()
);

-- Index pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_laps_session      ON raw.laps(session_key);
CREATE INDEX IF NOT EXISTS idx_laps_driver       ON raw.laps(acronym);
CREATE INDEX IF NOT EXISTS idx_laps_compound     ON raw.laps(compound);
CREATE INDEX IF NOT EXISTS idx_pit_session       ON raw.pit_stops(session_key);
CREATE INDEX IF NOT EXISTS idx_weather_session   ON raw.weather(session_key);
CREATE INDEX IF NOT EXISTS idx_results_year      ON raw.race_results(year, round);
CREATE INDEX IF NOT EXISTS idx_standings_year    ON raw.driver_standings(year, round);

COMMENT ON SCHEMA raw     IS 'Données brutes chargées par le pipeline ETL';
COMMENT ON SCHEMA staging IS 'Données nettoyées et typées par dbt';
COMMENT ON SCHEMA mart    IS 'Tables analytiques finales pour Streamlit';
