# pages/strategy.py — F1 Data Hub · Stratégie pneus
import sys, os as _os
_pages_dir = _os.path.dirname(_os.path.abspath(__file__))
_dash_dir  = _os.path.dirname(_pages_dir)
for _p in [_dash_dir, _pages_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_loader import get_laps, get_pit_stops, show_source_badge, TEAM_COLORS

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

TYRE_COLORS = {
    "SOFT":"#E8002D", "MEDIUM":"#FFD700", "HARD":"#D0D0D0",
    "INTERMEDIATE":"#39B54A", "WET":"#0093CC", "UNKNOWN":"#4A5570",
}

def show(session_key, n_laps: int, year: int=2024, round_num: int=1, circuit: str=None):
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
    df_laps = get_laps(session_key=session_key, year=year, round_num=round_num, n_laps=n_laps, circuit=circuit)
    df_pit  = get_pit_stops(session_key=session_key, year=year, round_num=round_num, circuit=circuit)

    st.markdown(f"""
    <div class="page-header">
        <div class="page-icon">🔧</div>
        <div>
            <div class="page-title">Stratégie pneus & pit stops</div>
            <div class="page-sub">Saison {year} · Manche {round_num:02d} · {n_laps} tours</div>
        </div>
    </div>""", unsafe_allow_html=True)

    show_source_badge(year=year, session_key=session_key)

    if df_laps.empty or "driver" not in df_laps.columns:
        st.warning("Données indisponibles.")
        return

    if df_pit.empty or "driver" not in df_pit.columns:
        df_pit = pd.DataFrame(columns=["session_key","driver","lap_number","pit_duration_s"])

    with st.sidebar:
        st.markdown("---")
        st.markdown('<p style="font-size:10px;color:#3A4A60;letter-spacing:.5px;text-transform:uppercase">Filtres stratégie</p>', unsafe_allow_html=True)
        all_drivers = sorted(df_laps["driver"].unique())
        sel = st.multiselect("Pilotes", all_drivers, default=all_drivers[:8], key="st_drv")

    if not sel:
        st.info("Sélectionnez au moins un pilote.")
        return

    df   = df_laps[df_laps["driver"].isin(sel)].copy()
    pits = df_pit[df_pit["driver"].isin(sel)].copy() if "driver" in df_pit.columns else df_pit.copy()

    c1, c2, c3, c4 = st.columns(4)
    def _kpi_pit(col, accent, label, value, sub, pct):
        html = (
            '<div class="kpi-card">'
            '<div class="kpi-accent" style="background:' + accent + '"></div>'
            '<div class="kpi-label">' + label + '</div>'
            '<div class="kpi-value">' + str(value) + '</div>'
            '<div class="kpi-sub">' + sub + '</div>'
            '<div class="kpi-bar"><div class="kpi-bar-fill" '
            'style="width:' + str(pct) + '%;background:' + accent + '"></div></div>'
            '</div>'
        )
        with col:
            st.markdown(html, unsafe_allow_html=True)

    _kpi_pit(c1, "#4AE8C0", "Arrêts aux stands", len(pits), "total course", 100)
    if len(pits):
        fp       = pits.loc[pits["pit_duration_s"].idxmin()]
        fp_drv   = str(fp["driver"])
        fp_dur   = f"{fp['pit_duration_s']:.2f}s"
        avg_dur  = f"{pits['pit_duration_s'].mean():.2f}s"
        max_dur  = f"{pits['pit_duration_s'].max():.2f}s"
        _kpi_pit(c2, "#E10600", "Pit le plus rapide", fp_drv,  fp_dur,   100)
        _kpi_pit(c3, "#FF8000", "Durée moyenne",       avg_dur, "par arrêt", 75)
        _kpi_pit(c4, "#9A7FDD", "Pit le plus lent",    max_dur, "durée max", 50)
    else:
        for col, lbl in [(c2,"Pit le plus rapide"),(c3,"Durée moyenne"),(c4,"Pit le plus lent")]:
            _kpi_pit(col, "#2A3448", lbl, "—", "", 0)

    # ── Gantt stints ──────────────────────────────────────────
    st.markdown('<div class="data-card"><div class="card-title">Stratégie par pilote <span class="card-badge">Gantt stints</span></div>', unsafe_allow_html=True)
    fig = go.Figure()
    compound_col = "compound" if "compound" in df.columns else None
    for drv in sel:
        d_drv = df[df["driver"]==drv].sort_values("lap_number")
        if d_drv.empty: continue
        stints, comp = [], d_drv.iloc[0].get("compound","UNKNOWN") if compound_col else "UNKNOWN"
        stint_start  = 1
        for _, row in d_drv.iterrows():
            cur = row.get("compound","UNKNOWN") if compound_col else "UNKNOWN"
            if cur != comp:
                stints.append((stint_start, int(row["lap_number"])-1, comp))
                stint_start, comp = int(row["lap_number"]), cur
        stints.append((stint_start, int(d_drv["lap_number"].max()), comp))
        for s, e, c in stints:
            clr = TYRE_COLORS.get(str(c).upper(), "#4A5570")
            fig.add_trace(go.Bar(
                x=[e-s+1], y=[drv], base=[s-1], orientation="h",
                marker=dict(color=clr, opacity=0.9, line=dict(width=0)),
                name=str(c), showlegend=False,
                hovertemplate=f"<b>{drv}</b><br>{c}<br>Tours {s}–{e}<extra></extra>",
            ))
    for comp, clr in TYRE_COLORS.items():
        if comp != "UNKNOWN":
            fig.add_trace(go.Bar(x=[0], y=[""], base=[0], orientation="h",
                                  marker_color=clr, name=comp, showlegend=True))
    fig.update_layout(**PLOT, height=max(300, len(sel)*45), barmode="overlay",
                      xaxis=dict(**AX, range=[0, n_laps], title="Tour"),
                      yaxis=dict(**AX_LIGHT),
                      legend=dict(bgcolor="#161B27", borderwidth=0.5,
                                  orientation="h", y=1.08,
                                  font=dict(color="#C8D4E8", size=12)))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="data-card"><div class="card-title">Durée des arrêts <span class="card-badge">par pilote</span></div>', unsafe_allow_html=True)
        if len(pits):
            pit_drv = pits.groupby("driver")["pit_duration_s"].mean().sort_values().reset_index()
            fig2 = go.Figure(go.Bar(
                x=pit_drv["pit_duration_s"], y=pit_drv["driver"],
                orientation="h", marker_color="#4A8FE0",
                text=[f"{v:.2f}s" for v in pit_drv["pit_duration_s"]],
                textposition="outside", textfont=dict(size=12, color="#FFFFFF"),
            ))
            fig2.update_layout(**PLOT, height=300,
                               xaxis=dict(**AX, title="Secondes"),
                               yaxis=dict(**AX_LIGHT), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Pas de données pit stops.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="data-card"><div class="card-title">Répartition des compounds <span class="card-badge">donut</span></div>', unsafe_allow_html=True)
        if compound_col and "compound" in df.columns:
            cc = df.groupby("compound")["lap_number"].count().reset_index()
            cc.columns = ["compound","tours"]
            clrs = [TYRE_COLORS.get(c.upper(),"#4A5570") for c in cc["compound"]]
            fig3 = go.Figure(go.Pie(
                labels=cc["compound"], values=cc["tours"],
                hole=0.55, marker_colors=clrs,
                textfont_size=12, textfont_color="#E8EDF5",
            ))
            fig3.update_layout(**PLOT, height=300, showlegend=True,
                               legend=dict(bgcolor="#161B27", borderwidth=0.5,
                                           font=dict(color="#C8D4E8")))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Données compounds non disponibles.")
        st.markdown('</div>', unsafe_allow_html=True)
