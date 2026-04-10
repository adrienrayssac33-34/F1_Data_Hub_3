# 🏎️ F1 Data Hub — Projet 3 · Wild Code School · D3M 2026

Plateforme d'analyse Formula 1 (2020–2025) construite avec un pipeline ETL complet,
une base PostgreSQL, des transformations dbt, une orchestration Airflow
et un dashboard Streamlit interactif.

---

## 📁 Structure du projet

```
f1_data_hub/
├── docker-compose.yml              ← Infrastructure complète
├── postgres/
│   └── init/01_init.sql            ← Schémas raw / staging / mart + tables
├── airflow/
│   └── dags/f1_pipeline_dag.py     ← DAG orchestrateur quotidien
├── etl/
│   ├── extractors/
│   │   ├── openf1_extractor.py     ← OpenF1 API (2023–2025)
│   │   ├── fastf1_extractor.py     ← FastF1 (2020–2022)
│   │   └── jolpica_extractor.py    ← Jolpica / Ergast (classements)
│   └── loaders/
│       └── postgres_loader.py      ← Chargement idempotent PostgreSQL
├── dbt/
│   ├── profiles.yml
│   ├── dbt_project.yml
│   └── models/
│       ├── sources.yml
│       ├── staging/                ← stg_sessions · stg_laps · stg_driver_standings
│       └── mart/                   ← mart_driver_performance · mart_team_performance · mart_season_overview
└── dashboard/
    ├── app.py                      ← Point d'entrée Streamlit
    ├── db.py                       ← Connexion PostgreSQL (SQLAlchemy)
    ├── Dockerfile
    ├── requirements.txt
    └── pages/
        ├── overview.py
        ├── lap_analysis.py
        ├── strategy.py
        ├── telemetry.py
        ├── weather.py
        └── ml_page.py
```

---

## 🚀 Lancement avec Docker (recommandé)

```bash
# 1. Cloner le projet
cd f1_data_hub

# 2. Lancer tous les services
docker compose up -d

# 3. Attendre ~30 secondes que PostgreSQL démarre

# 4. Accéder aux interfaces
# Airflow   : http://localhost:8080  (admin / admin)
# Streamlit : http://localhost:8501
# PostgreSQL: localhost:5432  (f1user / f1pass / f1_data_hub)
```

### Commandes utiles Docker

```bash
# Voir les logs Airflow
docker compose logs -f airflow-scheduler

# Arrêter tous les services
docker compose down

# Arrêter et supprimer les volumes (reset complet)
docker compose down -v

# Relancer un seul service
docker compose restart streamlit
```

---

## 💻 Lancement local sans Docker

### Streamlit

```bash
cd dashboard
pip install -r requirements.txt
py -m streamlit run app.py
```

### Airflow (nécessite Linux ou WSL2 sur Windows)

```bash
pip install apache-airflow psycopg2-binary

# Initialisation (une seule fois)
airflow db migrate
airflow users create \
  --username admin --password admin \
  --role Admin --firstname F1 --lastname Admin \
  --email admin@f1.local

# Terminal 1 — scheduler
airflow scheduler

# Terminal 2 — interface web
airflow webserver --port 8080
```

### dbt

```bash
pip install dbt-postgres
cd dbt
dbt debug          # vérifie la connexion
dbt run            # exécute les modèles
dbt test           # lance les tests
```

---

## 🌍 Sources de données

| Source | Saisons | Rôle | Accès |
|--------|---------|------|-------|
| FastF1 | 2020–2022 | Laps · météo · télémétrie | `pip install fastf1` |
| OpenF1 API | 2023–2025 | Laps · pit stops · météo | Connexion internet |
| Jolpica / Ergast | 2020–2025 | Classements · résultats · calendrier | Connexion internet · gratuit |

**Fallback automatique** : si l'API est indisponible, le dashboard bascule sur les données simulées.

---

## 🗄️ Modèle de données

```
raw.*          ← Données brutes chargées par l'ETL
  └── sessions · laps · drivers · pit_stops · weather
  └── driver_standings · team_standings

staging.*      ← Nettoyage + typage (vues dbt)
  └── stg_sessions · stg_laps · stg_driver_standings

mart.*         ← Tables analytiques finales (tables dbt)
  └── mart_driver_performance    KPIs pilote par course
  └── mart_team_performance      KPIs équipe par course
  └── mart_season_overview       Vue d'ensemble par saison
```

Streamlit lit **uniquement** les tables `mart.*` via SQLAlchemy.

---

## ⚙️ Pipeline Airflow

Le DAG `f1_pipeline` s'exécute tous les jours à 8h UTC :

```
extract_sessions
    ├── extract_laps       (OpenF1 ou FastF1 selon l'année)
    ├── extract_standings  (Jolpica)
    └── extract_weather    (OpenF1 2023+)
         └── quality_check
              └── dbt_run
                   └── dbt_test
```

---

## 📊 Pages du dashboard

| Page | Source | Contenu |
|------|--------|---------|
| Vue d'ensemble | mart.* | KPIs course · classement · meilleurs tours |
| Analyse des tours | mart.* | Temps · secteurs · dégradation pneus |
| Stratégie pneus | mart.* | Stints · pit stops · compounds |
| Télémétrie | raw.* | Comparaison vitesse/accel/frein (2 pilotes) |
| Météo & Circuit | raw.* | Températures · vent · carte circuit |
| Prédictions IA | mart.* | RandomForest · KMeans (bonus) |

---

## 🛠️ Stack technique

| Catégorie | Outil | Version |
|-----------|-------|---------|
| Orchestration | Apache Airflow | 2.9.1 |
| Base de données | PostgreSQL | 16 |
| Transformation | dbt-postgres | 1.8.0 |
| Interface | Streamlit | ≥ 1.35 |
| Visualisation | Plotly | ≥ 5.20 |
| Data | Pandas · NumPy | ≥ 2.0 · ≥ 1.26 |
| ML (bonus) | Scikit-learn | ≥ 1.4 |
| API F1 | FastF1 · OpenF1 · Jolpica | ≥ 3.3 |
| Infrastructure | Docker Compose | ≥ 2.0 |

---

## 👨‍💻 Auteurs

**Waguih YAHYA & Adrien**
Wild Code School · Bordeaux · Promotion D3M 2026
