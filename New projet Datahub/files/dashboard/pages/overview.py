# pages/overview.py — F1 Data Hub · Vue d'ensemble
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from data_loader import get_laps, get_pit_stops, get_standings, show_source_badge, TEAM_COLORS

PLOT = dict(
    paper_bgcolor="#161B27", plot_bgcolor="#0F1117",
    font=dict(color="#C8D8F0", size=12, family="Arial"),
    margin=dict(l=50, r=30, t=40, b=50),
)
AX = dict(gridcolor="#1E2535", linecolor="#2A3448", tickcolor="#2A3448")


def _drv(acronym: str) -> str:
    """Protège l'acronyme pilote contre la traduction du navigateur."""
    return f'<span translate="no" style="font-family:monospace">{acronym}</span>'


def _kpi(label, value, sub, color, pct=100):
    _p = int(min(100, max(0, pct)))
    st.markdown(
        '<div class="kpi-card">'
        '<div class="kpi-accent" style="background:' + color + '"></div>'
        '<div class="kpi-label">' + str(label) + '</div>'
        '<div class="kpi-value" translate="no">' + str(value) + '</div>'
        '<div class="kpi-sub">' + str(sub) + '</div>'
        '<div class="kpi-bar"><div class="kpi-bar-fill" style="width:' + str(_p) + '%;background:' + color + '"></div></div>'
        '</div>',
        unsafe_allow_html=True
    )


def show(session_key, gp_name: str, n_laps: int,
         year: int = 2024, round_num: int = 1, circuit: str = None):
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

    df_laps = get_laps(session_key=session_key, year=year,
                       round_num=round_num, n_laps=n_laps, circuit=circuit)
    df_pit  = get_pit_stops(session_key=session_key, year=year,
                            round_num=round_num, circuit=circuit)
    df_std  = get_standings(year=year)

    st.markdown(f"""
    <div class="page-header">
        <div class="page-icon">🏁</div>
        <div>
            <div class="page-title" translate="no">{gp_name}</div>
            <div class="page-sub">Saison {year} · Manche {round_num:02d} · {n_laps} tours · {circuit}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    show_source_badge(year=year, session_key=session_key)

    if df_laps.empty or "driver" not in df_laps.columns:
        st.warning("Données indisponibles pour cette session.")
        return

    # ── KPIs — toutes valeurs figées en str avant rendu ──────────
    _valid      = df_laps[df_laps["lap_time_s"].notna() & (df_laps["lap_time_s"] > 0)]
    if _valid.empty: _valid = df_laps
    fastest_idx = _valid["lap_time_s"].idxmin()
    fastest_drv = str(_valid.loc[fastest_idx, "driver"])
    mins, secs  = divmod(float(_valid.loc[fastest_idx, "lap_time_s"]), 60)
    lap_str     = f"{int(mins)}:{secs:06.3f}"
    _pit_col    = df_pit["pit_duration_s"].dropna() if not df_pit.empty and "pit_duration_s" in df_pit.columns else None
    avg_pit     = float(_pit_col.mean()) if _pit_col is not None and len(_pit_col) else 0.0
    n_drivers   = int(df_laps["driver"].nunique())
    n_teams     = int(df_laps["team"].nunique()) if "team" in df_laps.columns else 5
    champion    = str(df_std.iloc[0]["acronym"]) if not df_std.empty else "—"
    champ_pts   = int(df_std.iloc[0]["points"])  if not df_std.empty else 0
    champ_label = f"Champion {year}"
    champ_sub   = f"{champ_pts} pts"
    tours_sub   = f"{n_laps} t. · {n_drivers} pilotes"
    pit_sub     = f"moy. {avg_pit:.2f}s"
    pct_tours   = int(min(100, len(df_laps) * 100 // max(1, n_laps * n_drivers)))
    pct_pits    = int(min(100, len(df_pit) * 5))
    pct_teams   = int(min(100, n_teams * 20))

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: _kpi(champ_label,    champion,          champ_sub,  "#E10600", 100)
    with c2: _kpi("Meilleur tour", fastest_drv,      lap_str,    "#4A8FE0", 100)
    with c3: _kpi("Tours analysés", str(len(df_laps)), tours_sub, "#FF8000", pct_tours)
    with c4: _kpi("Pit stops",    str(len(df_pit)),  pit_sub,    "#4AE8C0", pct_pits)
    with c5: _kpi("Équipes",      str(n_teams),      "en course","#9A7FDD", pct_teams)

    st.markdown("---")

    # ── Ligne 1 : Box plot + Classement championnat ───────────
    col1, col2 = st.columns([1.1, 0.9])

    with col1:
        st.markdown('<div class="data-card"><div class="card-title">Temps au tour par pilote <span class="card-badge">box plot</span></div>', unsafe_allow_html=True)
        drivers = df_laps["driver"].unique()[:10]
        colors  = [
            TEAM_COLORS.get(df_laps[df_laps["driver"] == d]["team"].iloc[0], "#4A8FE0")
            if "team" in df_laps.columns else "#4A8FE0"
            for d in drivers
        ]
        fig = go.Figure()
        for drv, col in zip(drivers, colors):
            d = df_laps[df_laps["driver"] == drv]["lap_time_s"].dropna()
            fig.add_trace(go.Box(
                y=d, name=drv,
                marker_color=col, line_width=1.5,
                boxmean=True,
            ))
        fig.update_layout(**PLOT, height=360, showlegend=False,
                          xaxis=dict(**AX, tickfont=dict(color="#C8D4E8", size=12)),
                          yaxis=dict(**AX, title="Temps (s)"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="data-card"><div class="card-title">Classement championnat {year} <span class="card-badge">top 10</span></div>', unsafe_allow_html=True)
        if not df_std.empty:
            top10 = df_std.head(10).copy()
            # Couleurs équipes
            eq_colors = {
                "Red Bull Racing": "#3671C6",
                "Ferrari":         "#E8002D",
                "McLaren":         "#FF8000",
                "Mercedes":        "#27F4D2",
                "Aston Martin":    "#358C75",
                "Alpine":          "#0093CC",
                "Williams":        "#64C4FF",
                "RB":              "#5E8FAA",
                "Haas":            "#B6BABD",
                "Sauber":          "#52E252",
            }
            bar_clrs = [eq_colors.get(t, "#4A8FE0") for t in top10.get("team", ["—"] * len(top10))]

            fig2 = go.Figure(go.Bar(
                x=top10["acronym"],
                y=top10["points"],
                marker_color=bar_clrs,
                text=top10["points"],
                textposition="outside",
                textfont=dict(size=12, color="#FFFFFF"),
            ))
            fig2.update_layout(**PLOT, height=360, showlegend=False,
                               xaxis=dict(**AX, tickfont=dict(color="#C8D4E8", size=12)),
                               yaxis=dict(**AX, title="Points",
                                          tickfont=dict(color="#C8D8F0", size=11)))
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Ligne 2 : Évolution meilleur tour (pleine largeur) ────
    st.markdown('<div class="data-card"><div class="card-title">Évolution du meilleur tour au fil de la course <span class="card-badge">par tour</span></div>', unsafe_allow_html=True)
    best_by_lap = df_laps.groupby("lap_number")["lap_time_s"].min().reset_index()
    fig3 = px.line(best_by_lap, x="lap_number", y="lap_time_s",
                   color_discrete_sequence=["#E10600"])
    fig3.update_traces(line_width=3)
    fig3.add_scatter(
        x=best_by_lap["lap_number"],
        y=best_by_lap["lap_time_s"],
        mode="markers",
        marker=dict(size=5, color="#E10600"),
        showlegend=False,
    )
    fig3.update_layout(**PLOT, height=280,
                       xaxis=dict(**AX, title="Numéro de tour",
                                  tickfont=dict(color="#C8D8F0", size=11)),
                       yaxis=dict(**AX, title="Temps (secondes)",
                                  tickfont=dict(color="#C8D8F0", size=11)))
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Ligne 3 : Meilleurs temps par pilote (barres) ─────────
    st.markdown('<div class="data-card"><div class="card-title">Meilleur tour par pilote <span class="card-badge">classement</span></div>', unsafe_allow_html=True)
    best_per_drv = (
        df_laps.groupby("driver")["lap_time_s"]
        .min()
        .reset_index()
        .sort_values("lap_time_s")
    )
    if "team" in df_laps.columns:
        best_per_drv = best_per_drv.merge(
            df_laps[["driver", "team"]].drop_duplicates("driver"),
            on="driver", how="left"
        )
        bar_clrs2 = [TEAM_COLORS.get(t, "#4A8FE0") for t in best_per_drv.get("team", [])]
    else:
        bar_clrs2 = ["#4A8FE0"] * len(best_per_drv)

    fig4 = go.Figure(go.Bar(
        y=best_per_drv["driver"],
        x=best_per_drv["lap_time_s"],
        orientation="h",
        marker_color=bar_clrs2,
        text=[f"{t:.3f}s" for t in best_per_drv["lap_time_s"]],
        textposition="outside",
        textfont=dict(size=12, color="#FFFFFF"),
    ))
    fig4.update_layout(**PLOT, height=max(300, len(best_per_drv) * 38),
                       showlegend=False,
                       xaxis=dict(**AX, title="Temps (s)",
                                  tickfont=dict(color="#C8D8F0", size=11)),
                       yaxis=dict(**AX, tickfont=dict(color="#C8D4E8", size=12)))
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
