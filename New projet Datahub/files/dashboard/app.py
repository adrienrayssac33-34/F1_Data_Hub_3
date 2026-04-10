# dashboard/app.py — F1 Data Hub · Projet 3 · Wild Code School
# ════════════════════════════════════════════════════════════════
#  Lancement : cd dashboard && streamlit run app.py
# ════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import sys, os, importlib, math

_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

from data_loader import get_sessions, get_available_seasons

st.set_page_config(
    page_title="F1 Data Hub",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Fond principal ─────────────────────── */
.stApp { background: #0F1117 !important; }
.main .block-container { background: #0F1117 !important; padding-top: 1.5rem; }

/* ── Sidebar ────────────────────────────── */
[data-testid="stSidebar"] {
    background: #161B27 !important;
    border-right: 1px solid #1E2535;
}
[data-testid="stSidebar"] * { color: #C8D4E8 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label {
    color: #3A4A60 !important;
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: .5px;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #1E2535 !important;
    border: 0.5px solid #2A3448 !important;
    border-radius: 7px !important;
    color: #C8D4E8 !important;
    font-size: 12px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: #4A5A70 !important; }

/* ── KPI cards ──────────────────────────── */
.kpi-card {
    background: #161B27;
    border: 0.5px solid #1E2535;
    border-radius: 12px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
}
.kpi-accent { position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.kpi-label  { font-size: 10px; color: #F0C040; letter-spacing: .7px; text-transform: uppercase; margin-bottom: 7px; font-weight: 500; }
.kpi-value  { font-size: 28px; font-weight: 700; color: #FFFFFF; line-height: 1; }
.kpi-sub    { font-size: 11px; color: #C8D8F0; margin-top: 5px; }
.kpi-bar    { height: 3px; background: #252E3F; border-radius: 2px; margin-top: 10px; }
.kpi-bar-fill { height: 100%; border-radius: 2px; }

/* ── Data cards ─────────────────────────── */
.data-card {
    background: #161B27;
    border: 0.5px solid #252E3F;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 14px;
}
.card-title {
    font-size: 13px; font-weight: 600; color: #F0C040;
    margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
}
.card-badge {
    font-size: 10px; background: #252E3F;
    color: #C8D8F0; padding: 2px 8px;
    border-radius: 8px; font-weight: 400;
}

/* ── Metric container ───────────────────── */
[data-testid="metric-container"] {
    background: #161B27 !important;
    border: 0.5px solid #252E3F !important;
    border-radius: 12px !important;
    padding: 16px 18px !important;
}
[data-testid="metric-container"] label {
    color: #F0C040 !important;
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: .4px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 28px !important;
    font-weight: 700 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 12px !important;
    color: #C8D8F0 !important;
}

/* ── Page header ────────────────────────── */
.page-header {
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 24px; padding-bottom: 16px;
    border-bottom: 1px solid #1E2535;
}
.page-icon {
    width: 42px; height: 42px;
    background: #E10600; border-radius: 10px;
    display: flex; align-items: center;
    justify-content: center; font-size: 20px;
    flex-shrink: 0;
}
.page-title { font-size: 20px; font-weight: 600; color: #FFFFFF; }
.page-sub   { font-size: 11px; color: #C8D8F0; margin-top: 3px; }

/* ── F1 badge ───────────────────────────── */
.f1-badge {
    display: inline-block;
    background: #E10600; color: #fff;
    font-size: 9px; font-weight: 600;
    padding: 3px 8px; border-radius: 4px;
    letter-spacing: .5px;
}

/* ── GP info box ────────────────────────── */
.gp-box {
    background: #1E2535;
    border: 0.5px solid #2A3448;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 8px;
}

/* ── Source badges ──────────────────────── */
.src-badge {
    display: inline-block;
    font-size: 10px; padding: 3px 10px;
    border-radius: 10px; margin-bottom: 14px;
    font-weight: 500;
}
.src-openf1 { background: #0D2B1A; color: #5AE890; border: 0.5px solid #1D5A34; }
.src-fastf1 { background: #1E1535; color: #C8A8F8; border: 0.5px solid #4A2880; }
.src-mock   { background: #1E1A0A; color: #F0C860; border: 0.5px solid #5A4A10; }

/* ── Tabs ───────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #161B27;
    border-bottom: 1px solid #1E2535;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; color: #4A5570;
    font-size: 12px; padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: #1E1520 !important;
    color: #E10600 !important;
    border-bottom: 2px solid #E10600 !important;
}

/* ── Divider ────────────────────────────── */
hr { border-color: #1E2535 !important; }

/* ── Prevent browser translation of driver names ── */
[data-notranslate], .notranslate { translate: no; }

/* ── Hide Streamlit chrome ──────────────── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"],
[data-testid="collapsedControl"],
div[class*="sidebarNavItems"],
nav[aria-label="main"] { display: none !important; }
section[data-testid="stSidebar"] > div:first-child { padding-top: 0.5rem !important; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Bloquer la traduction automatique du navigateur sur toute la page
st.markdown('''
<meta name="google" content="notranslate">
<meta http-equiv="Content-Language" content="fr">
<script>
// Empêcher Chrome de proposer/appliquer la traduction
Object.defineProperty(document.documentElement, 'lang', {value: 'fr'});
document.documentElement.setAttribute('translate', 'no');
document.documentElement.classList.add('notranslate');
// Bloquer l'API de traduction de Chrome
if (window.chrome && window.chrome.runtime) {
    try { window.chrome.runtime.sendMessage = () => {}; } catch(e) {}
}
</script>
''', unsafe_allow_html=True)


def _clean_key(val):
    if val is None:
        return None
    try:
        f = float(val)
        return None if math.isnan(f) else int(f)
    except (TypeError, ValueError):
        return None


# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:

    st.markdown('<span class="f1-badge">F1 DATA HUB</span>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:13px;font-weight:600;color:#E8EDF5;margin:8px 0 2px">Dashboard · Projet 3</p>'
        '<p style="font-size:10px;color:#4A5570;margin:0">Formation Data Analyst · 2026</p>',
        unsafe_allow_html=True,
    )
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏁  Vue d'ensemble",
            "🏆  Classement pilotes",
            "📊  Analyse des tours",
            "🔧  Stratégie pneus",
            "📡  Télémétrie",
            "🌦️  Météo & Circuit",
            "🤖  Prédictions IA",
        ],
        label_visibility="collapsed",
    )
    st.divider()

    seasons = get_available_seasons()
    selected_season = st.selectbox(
        "📅  Saison",
        options=seasons,
        index=seasons.index(2024) if 2024 in seasons else 0,
        format_func=lambda y: f"Saison {y}",
        key="sel_season",
    )

    sessions_df = get_sessions(season=selected_season)
    gp_labels = [
        f"R{row['round']:02d}  ·  {row['gp_name']}"
        for _, row in sessions_df.iterrows()
    ]

    selected_gp_index = st.selectbox(
        "🏁  Grand Prix",
        options=list(range(len(gp_labels))),
        format_func=lambda i: gp_labels[i],
        index=0,
        key="sel_gp",
    )

    _row        = sessions_df.iloc[selected_gp_index]
    gp_name     = str(_row["gp_name"])
    n_laps      = int(_row["laps"])
    circuit     = str(_row["circuit"])
    country     = str(_row["country"])
    date        = str(_row["date"])
    track_km    = float(_row["track_km"])
    year        = int(_row["year"])
    round_num   = int(_row["round"])
    session_key = _clean_key(_row["session_key"])

    if session_key:
        src_html = f'<span style="font-size:9px;background:#0D2B1A;color:#4AE88A;padding:2px 7px;border-radius:6px;border:0.5px solid #1D5A34">OpenF1 · {session_key}</span>'
    elif year >= 2023:
        src_html = '<span style="font-size:9px;background:#0D2B1A;color:#4AE88A;padding:2px 7px;border-radius:6px;border:0.5px solid #1D5A34">OpenF1 · auto</span>'
    else:
        src_html = f'<span style="font-size:9px;background:#1E1535;color:#C4A0F0;padding:2px 7px;border-radius:6px;border:0.5px solid #4A2880">FastF1 · {year} R{round_num:02d}</span>'

    st.markdown(f"""
    <div class="gp-box">
        <div style="font-size:13px;font-weight:600;color:#E8EDF5;margin-bottom:4px"
             translate="no">{gp_name}</div>
        <div style="font-size:10px;color:#4A5570">{circuit} · {n_laps} tours · {date}</div>
        <div style="margin-top:8px;display:flex;gap:5px;flex-wrap:wrap">
            {src_html}
            <span style="font-size:9px;background:#1E2535;color:#4A5570;padding:2px 7px;border-radius:6px;border:0.5px solid #2A3448">R{round_num:02d}</span>
            <span style="font-size:9px;background:#0D1E35;color:#5A9AE0;padding:2px 7px;border-radius:6px;border:0.5px solid #1A3A6A">{year}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown(
        '<p style="font-size:9px;color:#2A3A50;margin:0">Sources : OpenF1 · FastF1</p>'
        '<p style="font-size:9px;color:#2D6A44;margin:4px 0 0">● Production 2020–2025</p>',
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════════════════════════
# session_row
# ════════════════════════════════════════════════════════════════
session_row = pd.Series({
    "session_key": session_key,
    "gp_name":     gp_name,
    "circuit":     circuit,
    "country":     country,
    "date":        date,
    "laps":        n_laps,
    "track_km":    track_km,
    "year":        year,
    "round":       round_num,
})

# ════════════════════════════════════════════════════════════════
# ROUTING
# ════════════════════════════════════════════════════════════════
for _mod in [k for k in sys.modules if k.startswith("pages.")]:
    del sys.modules[_mod]

if page == "🏁  Vue d'ensemble":
    import pages.overview as _m
    importlib.reload(_m)
    _m.show(session_key, gp_name, n_laps, year, round_num, circuit)

elif page == "🏆  Classement pilotes":
    import pages.standings as _m
    importlib.reload(_m)
    _m.show()

elif page == "📊  Analyse des tours":
    import pages.lap_analysis as _m
    importlib.reload(_m)
    _m.show(session_key, n_laps, year, round_num, circuit)

elif page == "🔧  Stratégie pneus":
    import pages.strategy as _m
    importlib.reload(_m)
    _m.show(session_key, n_laps, year, round_num, circuit)

elif page == "📡  Télémétrie":
    import pages.telemetry as _m
    importlib.reload(_m)
    _m.show(year, round_num)

elif page == "🌦️  Météo & Circuit":
    import pages.weather as _m
    importlib.reload(_m)
    _m.show(session_key, session_row)

elif page == "🤖  Prédictions IA":
    import pages.ml_page as _m
    importlib.reload(_m)
    _m.show(session_key, n_laps, year, round_num, circuit)
