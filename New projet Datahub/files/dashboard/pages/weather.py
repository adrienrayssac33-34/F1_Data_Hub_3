# pages/weather.py — F1 Data Hub · Météo & Circuit
import sys, os as _os
_pages_dir = _os.path.dirname(_os.path.abspath(__file__))
_dash_dir  = _os.path.dirname(_pages_dir)
for _p in [_dash_dir, _pages_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
import plotly.graph_objects as go
import data_loader as _dl
from data_loader import show_source_badge, CIRCUIT_COORDS, hex_to_rgba

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


def _wx_card(col, val, unit, label, color):
    """KPI météo — construit le HTML sans f-string imbriquée."""
    html = (
        '<div class="kpi-card">'
        '<div class="kpi-accent" style="background:' + color + '"></div>'
        '<div class="kpi-label" style="white-space:nowrap;overflow:hidden;'
        'text-overflow:ellipsis;font-size:10px">' + label + '</div>'
        '<div class="kpi-value">' + str(val)
        + ' <span style="font-size:14px;color:#8AA0BC">' + unit + '</span></div>'
        '<div class="kpi-bar"><div class="kpi-bar-fill" '
        'style="width:100%;background:' + color + '"></div></div>'
        '</div>'
    )
    with col:
        st.markdown(html, unsafe_allow_html=True)


def show(session_key, session_row):

    st.markdown("""
    <style>
    .kpi-label  { color: #F0C040 !important; font-size: 10px !important;
                  font-weight: 600 !important; text-transform: uppercase !important;
                  white-space: nowrap !important; overflow: hidden !important;
                  text-overflow: ellipsis !important; }
    .kpi-value  { color: #FFFFFF !important; font-size: 26px !important;
                  font-weight: 700 !important; }
    .kpi-sub    { color: #C8D8F0 !important; }
    .card-title { color: #F0C040 !important; font-weight: 600 !important; }
    .card-badge { color: #C8D8F0 !important; background: #252E3F !important; }
    .page-title { color: #FFFFFF !important; }
    .page-sub   { color: #C8D8F0 !important; }
    </style>
    """, unsafe_allow_html=True)

    circuit   = str(session_row["circuit"])
    gp_name   = str(session_row["gp_name"])
    year      = int(session_row.get("year", 2024))
    round_num = int(session_row.get("round", 1))
    n_points  = int(session_row.get("laps", 57))

    st.markdown(
        '<div class="page-header">'
        '<div class="page-icon">🌦️</div>'
        '<div>'
        '<div class="page-title">' + gp_name + ' — Météo &amp; Circuit</div>'
        '<div class="page-sub">' + circuit + ' · Saison ' + str(year)
        + ' · Manche ' + f"{round_num:02d}" + '</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    show_source_badge(year=year, session_key=session_key)

    # ── Chargement météo — robuste 2020-2025 ───────────────────
    df_wx = None
    try:
        df_wx = _dl.get_weather(
            session_key=session_key, year=year,
            round_num=round_num, n_points=n_points, circuit=circuit
        )
    except Exception as e:
        st.warning(f"Impossible de charger les données météo : {e}")
        return

    if df_wx is None or df_wx.empty:
        st.warning("Données météo indisponibles pour cette session.")
        return

    # Colonnes garanties — valeurs par défaut si absentes (FastF1 < 2023)
    _WX_DEFAULTS = {
        "air_temperature":   20.0,
        "track_temperature": 30.0,
        "humidity":          50.0,
        "wind_speed":        0.0,
        "rainfall":          0.0,
    }
    for col, default in _WX_DEFAULTS.items():
        if col not in df_wx.columns:
            df_wx[col] = default

    # ── KPI météo ──────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    rain = df_wx["rainfall"].sum()

    _wx_card(c1, f"{df_wx['air_temperature'].mean():.1f}°",   "C",    "Air",         "#FF8000")
    _wx_card(c2, f"{df_wx['track_temperature'].mean():.1f}°", "C",    "Piste",       "#E10600")
    _wx_card(c3, f"{df_wx['humidity'].mean():.0f}",           "%",    "Humidité",    "#4A8FE0")
    _wx_card(c4, f"{df_wx['wind_speed'].mean():.1f}",         "km/h", "Vent",        "#4AE8C0")
    _wx_card(c5, "Oui" if rain > 0 else "Non", "",            "Pluie",
             "#9A7FDD" if rain > 0 else "#2A3448")

    # ── Évolution températures ─────────────────────────────────
    st.markdown(
        '<div class="data-card">'
        '<div class="card-title">Évolution des températures '
        '<span class="card-badge">course</span></div>',
        unsafe_allow_html=True
    )
    x = list(range(len(df_wx)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=df_wx["track_temperature"], name="Piste",
        line=dict(color="#E10600", width=3),
        fill="tozeroy", fillcolor=hex_to_rgba("#E10600", 0.12)
    ))
    fig.add_trace(go.Scatter(
        x=x, y=df_wx["air_temperature"], name="Air",
        line=dict(color="#FF8000", width=3),
        fill="tozeroy", fillcolor=hex_to_rgba("#FF8000", 0.12)
    ))
    fig.update_layout(
        **PLOT, height=300,
        xaxis=dict(**AX, title="Point de mesure"),
        yaxis=dict(**AX, title="Température (°C)"),
        legend=dict(bgcolor="#161B27", borderwidth=0.5,
                    font=dict(color="#C8D8F0", size=12))
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # ── Humidité & Vent ────────────────────────────────────────
    with col1:
        st.markdown(
            '<div class="data-card">'
            '<div class="card-title">Humidité &amp; Vent '
            '<span class="card-badge">double axe</span></div>',
            unsafe_allow_html=True
        )
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=x, y=df_wx["humidity"], name="Humidité %",
            line=dict(color="#4A8FE0", width=2.5), yaxis="y"
        ))
        fig2.add_trace(go.Scatter(
            x=x, y=df_wx["wind_speed"], name="Vent km/h",
            line=dict(color="#4AE8C0", width=2.5), yaxis="y2"
        ))
        fig2.update_layout(
            **PLOT, height=300,
            yaxis=dict(**AX, title="Humidité (%)"),
            yaxis2=dict(
                title="Vent (km/h)", overlaying="y", side="right",
                tickfont=dict(color="#C8D8F0", size=11)
            ),
            legend=dict(bgcolor="#161B27", borderwidth=0.5,
                        font=dict(color="#C8D8F0"))
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Localisation & infos circuit ───────────────────────────
    with col2:
        st.markdown(
            '<div class="data-card">'
            '<div class="card-title">Localisation du circuit</div>',
            unsafe_allow_html=True
        )
        coords = CIRCUIT_COORDS.get(circuit)
        if coords:
            import pandas as pd
            df_map = pd.DataFrame({
                "lat": [coords[0]], "lon": [coords[1]], "circuit": [circuit]
            })
            st.map(df_map, latitude="lat", longitude="lon",
                   size=30000, color="#E10600")
        else:
            st.info(f"Coordonnées non disponibles pour {circuit}.")

        infos = {
            "Circuit":  circuit,
            "Longueur": str(session_row.get("track_km", "—")) + " km",
            "Tours":    str(n_points),
            "Pays":     str(session_row.get("country", "—")),
            "Date":     str(session_row.get("date", "—")),
        }
        for k, v in infos.items():
            row_html = (
                '<div style="display:flex;justify-content:space-between;'
                'padding:6px 0;border-bottom:0.5px solid #1E2535;font-size:12px">'
                '<span style="color:#F0C040;font-weight:500">' + k + '</span>'
                '<span style="color:#FFFFFF">' + v + '</span>'
                '</div>'
            )
            st.markdown(row_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
