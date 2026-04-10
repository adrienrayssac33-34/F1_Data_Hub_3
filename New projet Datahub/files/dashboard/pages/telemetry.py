# pages/telemetry.py — F1 Data Hub · Télémétrie comparative
import sys, os as _os
_pages_dir = _os.path.dirname(_os.path.abspath(__file__))
_dash_dir  = _os.path.dirname(_pages_dir)
for _p in [_dash_dir, _pages_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
import streamlit as st
import plotly.graph_objects as go
from data_loader import get_telemetry, show_source_badge, DRIVERS_2024, DRIVER_COLORS, hex_to_rgba

PLOT = dict(
    paper_bgcolor="#161B27", plot_bgcolor="#0F1117",
    font=dict(color="#C8D8F0", size=12, family="Arial"),
    margin=dict(l=50, r=30, t=40, b=50),
)
AX = dict(
    gridcolor="#1E2A3A", linecolor="#2A3850",
    tickcolor="#2A3850",
    tickfont=dict(color="#C8D8F0", size=11),
)
AX_LIGHT = dict(
    gridcolor="#1E2A3A", linecolor="#2A3850",
    tickcolor="#2A3850",
    tickfont=dict(color="#D0DDF0", size=12),
)

def show(year: int = 2024, round_num: int = 1):
    # CSS forcé — couleurs lisibles sur fond sombre
    st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background: #161B27 !important;
        border: 0.5px solid #252E3F !important;
        border-radius: 12px !important;
        padding: 16px 18px !important;
    }
    div[data-testid="metric-container"] > label,
    div[data-testid="metric-container"] > div > label,
    div[data-testid="stMetricLabel"] > div > p,
    div[data-testid="stMetricLabel"] p {
        color: #F0C040 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: .5px !important;
        opacity: 1 !important;
    }
    div[data-testid="stMetricValue"] > div,
    div[data-testid="stMetricValue"] p,
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    div[data-testid="stMetricDelta"] > div,
    div[data-testid="stMetricDelta"] p {
        color: #C8E8FF !important;
        font-size: 12px !important;
        opacity: 1 !important;
    }
    .kpi-label  { color: #F0C040 !important; font-size: 11px !important; font-weight: 600 !important; }
    .kpi-value  { color: #FFFFFF !important; font-size: 28px !important; font-weight: 700 !important; }
    .kpi-sub    { color: #C8D8F0 !important; font-size: 11px !important; }
    .card-title { color: #F0C040 !important; font-size: 13px !important; font-weight: 600 !important; }
    .card-badge { color: #C8D8F0 !important; background: #252E3F !important; }
    .page-title { color: #FFFFFF !important; }
    .page-sub   { color: #C8D8F0 !important; }
    </style>
    """, unsafe_allow_html=True)
    drivers = [d["acronym"] for d in DRIVERS_2024] if DRIVERS_2024 else \
              ["VER","LEC","SAI","NOR","PIA","HAM","RUS","ALO","PER","STR",
               "GAS","OCO","TSU","RIC","BOT","ZHO","MAG","HUL","LAW","BEA"]

    st.markdown("""
    <div class="page-header">
        <div class="page-icon">📡</div>
        <div>
            <div class="page-title">Télémétrie comparative</div>
            <div class="page-sub">Vitesse · Accélérateur · Frein · Rapport</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<span class="src-badge src-mock">🟡 Données simulées</span>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("---")
        st.markdown('<p style="font-size:10px;color:#3A4A60;letter-spacing:.5px;text-transform:uppercase">Télémétrie</p>', unsafe_allow_html=True)
        drv_a = st.selectbox("Pilote A", drivers, index=0, key="tel_a")
        drv_b = st.selectbox("Pilote B", [d for d in drivers if d != drv_a], index=0, key="tel_b")
        st.slider("Tour à comparer", 1, 57, 25, key="tel_lap")

    # Pré-calcul complet AVANT tout rendu — évite le removeChild DOM
    col_a = DRIVER_COLORS.get(drv_a, "#4A8FE0")
    col_b = DRIVER_COLORS.get(drv_b, "#E10600")

    df_a = get_telemetry(drv_a, laps=1, year=year, round_num=round_num)
    df_b = get_telemetry(drv_b, laps=1, year=year, round_num=round_num)

    if df_a.empty or df_b.empty:
        st.warning("Données de télémétrie non disponibles.")
        return

    vmax_a = float(df_a["speed_kmh"].max()) if "speed_kmh" in df_a.columns else 0.0
    vmax_b = float(df_b["speed_kmh"].max()) if "speed_kmh" in df_b.columns else 0.0
    diff   = vmax_b - vmax_a
    sign   = "+" if diff >= 0 else ""
    pct_b  = int(min(100, vmax_b / max(1, vmax_a) * 100))
    acc_a  = float(df_a["throttle_pct"].mean()) if "throttle_pct" in df_a.columns else 0.0
    acc_b  = float(df_b["throttle_pct"].mean()) if "throttle_pct" in df_b.columns else 0.0
    acc_a_pct = int(min(100, acc_a))
    acc_b_pct = int(min(100, acc_b))

    # KPI HTML entièrement pré-calculé — valeurs figées avant st.markdown()
    def _kpi(col, accent, label, value, sub, pct):
        pct_int = int(min(100, max(0, pct)))
        html = (
            '<div class="kpi-card">'
            '<div class="kpi-accent" style="background:' + accent + '"></div>'
            '<div class="kpi-label">' + label + '</div>'
            '<div class="kpi-value">' + value + '</div>'
            '<div class="kpi-sub">' + sub + '</div>'
            '<div class="kpi-bar"><div class="kpi-bar-fill" '
            'style="width:' + str(pct_int) + '%;background:' + accent + '"></div></div>'
            '</div>'
        )
        with col:
            st.markdown(html, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    _kpi(c1, col_a, "Vmax " + drv_a, f"{vmax_a:.0f} km/h", "", 100)
    _kpi(c2, col_b, "Vmax " + drv_b, f"{vmax_b:.0f} km/h",
         sign + f"{diff:.0f} km/h vs " + drv_a, pct_b)
    _kpi(c3, col_a, "Accel. moy. " + drv_a, f"{acc_a:.0f}%", "", acc_a_pct)
    _kpi(c4, col_b, "Accel. moy. " + drv_b, f"{acc_b:.0f}%", "", acc_b_pct)

    channels = []
    if "speed_kmh"    in df_a.columns: channels.append(("speed_kmh",    "Vitesse (km/h)"))
    if "throttle_pct" in df_a.columns: channels.append(("throttle_pct", "Accélérateur (%)"))
    if "brake_pct"    in df_a.columns: channels.append(("brake_pct",    "Frein (%)"))
    if "gear"         in df_a.columns: channels.append(("gear",          "Rapport"))

    for canal, label in channels:
        st.markdown(f'<div class="data-card"><div class="card-title">{label} <span class="card-badge">{drv_a} vs {drv_b}</span></div>', unsafe_allow_html=True)
        fig = go.Figure()
        x = list(range(len(df_a)))
        fig.add_trace(go.Scatter(
            x=x, y=df_a[canal], name=drv_a,
            line=dict(color=col_a, width=3),
            fill="tozeroy", fillcolor=hex_to_rgba(col_a, 0.12),
        ))
        fig.add_trace(go.Scatter(
            x=x, y=df_b[canal], name=drv_b,
            line=dict(color=col_b, width=3),
            fill="tozeroy", fillcolor=hex_to_rgba(col_b, 0.12),
        ))
        fig.update_layout(**PLOT, height=240,
                          xaxis=dict(**AX, title="Distance (points)"),
                          yaxis=dict(**AX, title=label),
                          legend=dict(bgcolor="#161B27", borderwidth=0.5,
                                      orientation="h", y=1.1,
                                      font=dict(color="#C8D4E8", size=12)))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
