# pages/lap_analysis.py — F1 Data Hub · Analyse des tours
import sys, os as _os
_pages_dir = _os.path.dirname(_os.path.abspath(__file__))
_dash_dir  = _os.path.dirname(_pages_dir)
for _p in [_dash_dir, _pages_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from data_loader import get_laps, show_source_badge, TEAM_COLORS, COMPOUND_COLORS, hex_to_rgba

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
    df_all = get_laps(session_key=session_key, year=year, round_num=round_num, n_laps=n_laps, circuit=circuit)

    st.markdown(f"""
    <div class="page-header">
        <div class="page-icon">📊</div>
        <div>
            <div class="page-title">Analyse des tours</div>
            <div class="page-sub">Saison {year} · Manche {round_num:02d} · {n_laps} tours</div>
        </div>
    </div>""", unsafe_allow_html=True)

    show_source_badge(year=year, session_key=session_key)

    if df_all.empty or "driver" not in df_all.columns:
        st.warning("Données indisponibles pour cette session.")
        return

    with st.sidebar:
        st.markdown("---")
        st.markdown('<p style="font-size:10px;color:#3A4A60;letter-spacing:.5px;text-transform:uppercase">Filtres tours</p>', unsafe_allow_html=True)
        all_drivers = sorted(df_all["driver"].unique())
        sel_drivers = st.multiselect("Pilotes", all_drivers, default=all_drivers[:5], key="la_drv")
        lap_range   = st.slider("Tours", 1, n_laps, (1, n_laps), key="la_laps")

    if not sel_drivers:
        st.info("Sélectionnez au moins un pilote.")
        return

    df = df_all[df_all["driver"].isin(sel_drivers) &
                df_all["lap_number"].between(*lap_range)].copy()

    # ── KPIs — toutes valeurs pré-calculées avant st.markdown ────
    _valid = df[df["lap_time_s"].notna() & (df["lap_time_s"] > 0)]
    if _valid.empty:
        _valid = df
    best_row  = _valid.loc[_valid["lap_time_s"].idxmin()]
    mins, secs = divmod(float(best_row["lap_time_s"]), 60)
    best_drv  = str(best_row["driver"])
    lap_str   = f"{int(mins)}:{secs:06.3f}"
    avg_str   = f"{float(df['lap_time_s'].mean()):.3f}s"
    std_str   = f"s={float(df['lap_time_s'].std()):.3f}"
    n_tours   = str(len(df))
    n_pilots  = str(len(sel_drivers)) + " pilotes"
    _cpd      = str(df["compound"].mode()[0]) if "compound" in df.columns and len(df) else "—"
    _cpd_clr  = {"SOFT":"#E8002D","MEDIUM":"#FFD700","HARD":"#D0D0D0",
                 "INTERMEDIATE":"#39B54A","WET":"#0093CC"}.get(_cpd, "#9A7FDD")

    # HTML entièrement construit avant rendu
    def _kpi_html(accent, label, value, sub, pct):
        p = str(int(min(100, max(0, pct))))
        return (
            '<div class="kpi-card">'
            '<div class="kpi-accent" style="background:' + accent + '"></div>'
            '<div class="kpi-label">' + label + '</div>'
            '<div class="kpi-value">' + str(value) + '</div>'
            '<div class="kpi-sub">' + sub + '</div>'
            '<div class="kpi-bar"><div class="kpi-bar-fill" '
            'style="width:' + p + '%;background:' + accent + '"></div></div>'
            '</div>'
        )

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(_kpi_html("#E10600", "Meilleur tour",     best_drv, lap_str,  100), unsafe_allow_html=True)
    with c2: st.markdown(_kpi_html("#4A8FE0", "Temps moyen",       avg_str,  std_str,  80),  unsafe_allow_html=True)
    with c3: st.markdown(_kpi_html("#FF8000", "Tours analysés",    n_tours,  n_pilots, 70),  unsafe_allow_html=True)
    with c4: st.markdown(_kpi_html(_cpd_clr,  "Compound dominant", _cpd,     "pneu majoritaire", 90), unsafe_allow_html=True)

    # ── Évolution temps par tour (pleine largeur) ─────────────
    st.markdown('<div class="data-card"><div class="card-title">Temps au tour par pilote <span class="card-badge">ligne</span></div>', unsafe_allow_html=True)
    fig = go.Figure()
    for drv in sel_drivers:
        d   = df[df["driver"]==drv].sort_values("lap_number")
        col = TEAM_COLORS.get(d["team"].iloc[0], "#4A8FE0") if "team" in d.columns and len(d) else "#4A8FE0"
        fig.add_trace(go.Scatter(
            x=d["lap_number"], y=d["lap_time_s"], name=drv,
            mode="lines+markers",
            line=dict(color=col, width=2.5),
            marker=dict(size=4),
            hovertemplate=f"<b>{drv}</b><br>Tour %{{x}}<br>%{{y:.3f}}s<extra></extra>",
        ))
    fig.update_layout(**PLOT, height=380,
                      xaxis=dict(**AX, title="Numéro de tour"),
                      yaxis=dict(**AX, title="Temps (s)"),
                      legend=dict(bgcolor="#161B27", bordercolor="#1E2535",
                                  borderwidth=0.5, font=dict(color="#C8D4E8", size=12)))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="data-card"><div class="card-title">Meilleurs tours <span class="card-badge">classement</span></div>', unsafe_allow_html=True)
        best_per = df.groupby("driver")["lap_time_s"].min().sort_values().reset_index()
        bar_clrs = ["#E10600" if i==0 else "#4A8FE0" for i in range(len(best_per))]
        fig2 = go.Figure(go.Bar(
            x=best_per["lap_time_s"], y=best_per["driver"],
            orientation="h",
            marker_color=bar_clrs,
            text=[f"{t:.3f}s" for t in best_per["lap_time_s"]],
            textposition="outside",
            textfont=dict(size=12, color="#FFFFFF"),
        ))
        fig2.update_layout(**PLOT, height=320,
                           xaxis=dict(**AX, title="Temps (s)"),
                           yaxis=dict(**AX_LIGHT),
                           showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="data-card"><div class="card-title">Secteurs S1 · S2 · S3 <span class="card-badge">moyenne</span></div>', unsafe_allow_html=True)
        if all(c in df.columns for c in ["sector1_s","sector2_s","sector3_s"]):
            sec  = df.groupby("driver")[["sector1_s","sector2_s","sector3_s"]].mean().reset_index()
            fig3 = go.Figure()
            for s, col in [("sector1_s","#E10600"),("sector2_s","#4A8FE0"),("sector3_s","#FF8000")]:
                fig3.add_trace(go.Bar(
                    name=s.replace("_s","").upper(),
                    x=sec["driver"], y=sec[s],
                    marker_color=col,
                ))
            fig3.update_layout(**PLOT, height=320, barmode="stack",
                               xaxis=dict(**AX_LIGHT),
                               yaxis=dict(**AX, title="Temps (s)"),
                               legend=dict(bgcolor="#161B27", borderwidth=0.5,
                                           font=dict(color="#C8D4E8")))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Données secteurs non disponibles.")
        st.markdown('</div>', unsafe_allow_html=True)

    if "tyre_life" in df.columns:
        st.markdown('<div class="data-card"><div class="card-title">Dégradation pneus <span class="card-badge">temps vs tours sur pneu</span></div>', unsafe_allow_html=True)
        fig4 = px.scatter(
            df, x="tyre_life", y="lap_time_s", color="driver",
            color_discrete_sequence=["#E10600","#4A8FE0","#FF8000","#4AE8C0","#9A7FDD","#E878A0","#4AE888","#F0C050"],
            opacity=0.75,
            labels={"tyre_life":"Tours sur pneu","lap_time_s":"Temps (s)"},
        )
        fig4.update_traces(marker=dict(size=7))
        fig4.update_layout(**PLOT, height=300,
                           xaxis=dict(**AX, title="Tours sur pneu"),
                           yaxis=dict(**AX, title="Temps (s)"),
                           legend=dict(bgcolor="#161B27", borderwidth=0.5,
                                       font=dict(color="#C8D4E8")))
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
