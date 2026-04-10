# pages/standings.py — F1 Data Hub · Classement des pilotes 2020–2025
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from data_loader import get_standings

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
    tickfont=dict(color="#FFFFFF", size=12),
)

EQ_COLORS = {
    "Red Bull Racing": "#3671C6",
    "Ferrari":         "#E8002D",
    "McLaren":         "#FF8000",
    "Mercedes":        "#27F4D2",
    "Aston Martin":    "#358C75",
    "Alpine":          "#0093CC",
    "Williams":        "#64C4FF",
    "RB":              "#5E8FAA",
    "AlphaTauri":      "#5E8FAA",
    "Haas":            "#B6BABD",
    "Sauber":          "#52E252",
    "Alfa Romeo":      "#900000",
    "Racing Point":    "#F596C8",
    "Renault":         "#FFF500",
    "Toro Rosso":      "#469BFF",
}


def show():
    # ── CSS forcé ────────────────────────────────────────────
    st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background: #161B27 !important;
        border: 0.5px solid #252E3F !important;
        border-radius: 12px !important;
        padding: 16px 18px !important;
    }
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] > div > p {
        color: #F0C040 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        opacity: 1 !important;
    }
    div[data-testid="stMetricValue"] > div,
    div[data-testid="stMetricValue"] p {
        color: #FFFFFF !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    div[data-testid="stMetricDelta"] > div,
    div[data-testid="stMetricDelta"] p { color: #C8E8FF !important; }
    .kpi-label  { color: #F0C040 !important; font-weight: 600 !important; }
    .kpi-value  { color: #FFFFFF !important; font-weight: 700 !important; }
    .kpi-sub    { color: #C8D8F0 !important; }
    .card-title { color: #F0C040 !important; font-weight: 600 !important; }
    .card-badge { color: #C8D8F0 !important; background: #252E3F !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="page-header">
        <div class="page-icon">🏆</div>
        <div>
            <div class="page-title">Classement des pilotes</div>
            <div class="page-sub">Saisons 2020 → 2025 · Championnat du monde F1</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Sélecteur saison dans sidebar ────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<p style="font-size:10px;color:#F0C040;letter-spacing:.5px;'
            'text-transform:uppercase;font-weight:600">Classement</p>',
            unsafe_allow_html=True
        )
        selected_year = st.selectbox(
            "Saison",
            options=[2025, 2024, 2023, 2022, 2021, 2020],
            index=0,
            format_func=lambda y: f"Saison {y}",
            key="std_year",
        )

    df = get_standings(year=selected_year)
    if df.empty:
        st.warning("Données indisponibles.")
        return

    # ── KPIs saison ───────────────────────────────────────────
    champion   = df.iloc[0]["acronym"]
    champ_name = df.iloc[0]["name"]
    champ_team = df.iloc[0]["team"]
    champ_pts  = int(df.iloc[0]["points"])
    n_pilotes  = len(df)
    top3_pts   = int(df.iloc[2]["points"]) if len(df) >= 3 else 0
    gap_top2   = int(df.iloc[0]["points"] - df.iloc[1]["points"]) if len(df) >= 2 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Champion {selected_year}", champion, champ_name)
    c2.metric("Équipe championne", champ_team, f"{champ_pts} pts")
    c3.metric("Écart 1er → 2ème", f"{gap_top2} pts", f"{df.iloc[1]['acronym']} #{2}")
    c4.metric("Pilotes classés", str(n_pilotes), "top 15")

    st.markdown("---")

    # ── Onglets : Vue saison / Comparaison multi-saisons ─────
    tab1, tab2, tab3 = st.tabs(["  📊  Classement complet  ", "  📈  Évolution multi-saisons  ", "  🔄  Comparaison pilotes  "])

    # ════════════════════════════════════════════════════════
    # TAB 1 — Classement complet de la saison
    # ════════════════════════════════════════════════════════
    with tab1:
        col1, col2 = st.columns([1.2, 0.8])

        with col1:
            st.markdown(
                f'<div class="data-card"><div class="card-title">'
                f'Classement pilotes {selected_year} <span class="card-badge">points</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            bar_colors = [EQ_COLORS.get(t, "#4A8FE0") for t in df["team"]]
            fig = go.Figure(go.Bar(
                x=df["points"],
                y=df["acronym"],
                orientation="h",
                marker_color=bar_colors,
                text=[f"{int(p)} pts" for p in df["points"]],
                textposition="outside",
                textfont=dict(size=12, color="#FFFFFF"),
                customdata=df[["name", "team"]].values,
                hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{x} pts<extra></extra>",
            ))
            fig.update_layout(
                **PLOT, height=max(400, len(df) * 30),
                xaxis=dict(**AX, title="Points"),
                yaxis=dict(**AX_LIGHT, autorange="reversed"),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown(
                f'<div class="data-card"><div class="card-title">'
                f'Tableau détaillé <span class="card-badge">{selected_year}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            for _, row in df.iterrows():
                pos   = int(row["position"])
                acr   = row["acronym"]
                name  = row["name"]
                team  = row["team"]
                pts   = int(row["points"])
                clr   = EQ_COLORS.get(team, "#4A8FE0")
                pct   = int(pts / champ_pts * 100)
                medal = {1:"🥇", 2:"🥈", 3:"🥉"}.get(pos, f"{pos:2d}")
                bg    = "#1A1F2E" if pos % 2 == 0 else "#161B27"

                st.markdown(f"""
                <div style="background:{bg};border-radius:8px;padding:8px 12px;
                            margin-bottom:4px;display:flex;align-items:center;gap:10px">
                    <span style="font-size:14px;width:28px;text-align:center">{medal}</span>
                    <div style="flex:1">
                        <div style="font-size:13px;font-weight:700;color:#FFFFFF"
                             translate="no">{acr}</div>
                        <div style="font-size:10px;color:#8AA0BC">{name}</div>
                        <div style="font-size:9px;color:{clr};margin-top:1px">{team}</div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-size:16px;font-weight:700;color:#F0C040">{pts}</div>
                        <div style="width:60px;height:4px;background:#1E2A3A;
                                    border-radius:2px;margin-top:3px">
                            <div style="width:{pct}%;height:100%;background:{clr};border-radius:2px"></div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # TAB 2 — Évolution des points multi-saisons
    # ════════════════════════════════════════════════════════
    with tab2:
        st.markdown(
            '<div class="data-card"><div class="card-title">'
            'Points des champions par saison <span class="card-badge">2020 → 2025</span>'
            '</div>',
            unsafe_allow_html=True
        )

        # Récupérer tous les classements
        all_years = [2020, 2021, 2022, 2023, 2024, 2025]
        rows_all  = []
        for y in all_years:
            df_y = get_standings(year=y)
            for _, r in df_y.iterrows():
                rows_all.append({
                    "year":     y,
                    "acronym":  r["acronym"],
                    "name":     r["name"],
                    "team":     r["team"],
                    "points":   int(r["points"]),
                    "position": int(r["position"]),
                })
        df_all = pd.DataFrame(rows_all)

        # Champions par saison
        champions_df = df_all[df_all["position"] == 1].sort_values("year")

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=champions_df["year"],
            y=champions_df["points"],
            marker_color=[EQ_COLORS.get(t, "#4A8FE0") for t in champions_df["team"]],
            text=[f"{r['acronym']}<br>{r['points']} pts" for _, r in champions_df.iterrows()],
            textposition="inside",
            textfont=dict(size=12, color="#FFFFFF"),
            hovertemplate="<b>%{customdata[0]}</b><br>%{x}<br>%{y} pts<extra></extra>",
            customdata=champions_df[["name", "team"]].values,
        ))
        fig2.update_layout(
            **PLOT, height=320,
            xaxis=dict(**AX, title="Saison", dtick=1),
            yaxis=dict(**AX, title="Points du champion"),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Top 5 pilotes — évolution sur 6 saisons
        st.markdown(
            '<div class="data-card"><div class="card-title">'
            'Évolution points des top pilotes <span class="card-badge">top 5 récurrents</span>'
            '</div>',
            unsafe_allow_html=True
        )

        # Pilotes présents dans au moins 4 saisons
        pilot_counts = df_all.groupby("acronym")["year"].nunique()
        top_pilots   = pilot_counts[pilot_counts >= 3].nlargest(8).index.tolist()

        PILOT_COLORS = {
            "VER":"#3671C6", "HAM":"#27F4D2", "LEC":"#E8002D",
            "NOR":"#FF8000", "SAI":"#E8002D", "PER":"#3671C6",
            "RUS":"#27F4D2", "ALO":"#358C75", "PIA":"#FF8000",
            "BOT":"#27F4D2", "RIC":"#FF8000", "VET":"#358C75",
        }

        fig3 = go.Figure()
        for pilot in top_pilots:
            d = df_all[df_all["acronym"] == pilot].sort_values("year")
            clr = PILOT_COLORS.get(pilot, "#8AA0BC")
            fig3.add_trace(go.Scatter(
                x=d["year"], y=d["points"],
                name=pilot,
                mode="lines+markers",
                line=dict(color=clr, width=2.5),
                marker=dict(size=8, color=clr),
                hovertemplate=f"<b>{pilot}</b><br>%{{x}}<br>%{{y}} pts<extra></extra>",
            ))
        fig3.update_layout(
            **PLOT, height=350,
            xaxis=dict(**AX, title="Saison", dtick=1),
            yaxis=dict(**AX, title="Points"),
            legend=dict(bgcolor="#161B27", borderwidth=0.5,
                       font=dict(color="#C8D8F0", size=12),
                       orientation="h", y=-0.2),
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # TAB 3 — Comparaison directe entre pilotes
    # ════════════════════════════════════════════════════════
    with tab3:
        all_years2 = [2020, 2021, 2022, 2023, 2024, 2025]
        rows2 = []
        for y in all_years2:
            df_y = get_standings(year=y)
            for _, r in df_y.iterrows():
                rows2.append({
                    "year":     y,
                    "acronym":  r["acronym"],
                    "name":     r["name"],
                    "team":     r["team"],
                    "points":   int(r["points"]),
                    "position": int(r["position"]),
                })
        df2 = pd.DataFrame(rows2)

        all_pilots = sorted(df2["acronym"].unique())

        col_a, col_b = st.columns(2)
        with col_a:
            pilot_a = st.selectbox("Pilote A", all_pilots,
                                   index=all_pilots.index("VER") if "VER" in all_pilots else 0,
                                   key="cmp_a")
        with col_b:
            pilot_b = st.selectbox("Pilote B", [p for p in all_pilots if p != pilot_a],
                                   index=0, key="cmp_b")

        da = df2[df2["acronym"] == pilot_a].sort_values("year")
        db = df2[df2["acronym"] == pilot_b].sort_values("year")

        clr_a = PILOT_COLORS.get(pilot_a, "#4A8FE0")
        clr_b = PILOT_COLORS.get(pilot_b, "#E10600")

        st.markdown(
            f'<div class="data-card"><div class="card-title">'
            f'<span translate="no">{pilot_a}</span> vs '
            f'<span translate="no">{pilot_b}</span> — Points par saison</div>',
            unsafe_allow_html=True
        )

        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=da["year"], y=da["points"], name=pilot_a,
            marker_color=clr_a,
            text=da["points"], textposition="outside",
            textfont=dict(size=11, color="#FFFFFF"),
        ))
        fig4.add_trace(go.Bar(
            x=db["year"], y=db["points"], name=pilot_b,
            marker_color=clr_b,
            text=db["points"], textposition="outside",
            textfont=dict(size=11, color="#FFFFFF"),
        ))
        fig4.update_layout(
            **PLOT, height=340, barmode="group",
            xaxis=dict(**AX, title="Saison", dtick=1),
            yaxis=dict(**AX, title="Points"),
            legend=dict(bgcolor="#161B27", borderwidth=0.5,
                       font=dict(color="#C8D8F0", size=13)),
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Tableau récap comparatif
        st.markdown(
            '<div class="data-card"><div class="card-title">'
            'Résumé comparatif <span class="card-badge">toutes saisons</span>'
            '</div>',
            unsafe_allow_html=True
        )

        merged = da[["year","points","position","team"]].merge(
            db[["year","points","position","team"]],
            on="year", suffixes=(f"_{pilot_a}", f"_{pilot_b}"), how="outer"
        ).sort_values("year")

        # Header
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:60px 1fr 1fr;
                    gap:8px;padding:8px 12px;margin-bottom:4px">
            <div style="font-size:11px;color:#F0C040;font-weight:600">Saison</div>
            <div style="font-size:11px;color:{clr_a};font-weight:600"
                 translate="no">{pilot_a}</div>
            <div style="font-size:11px;color:{clr_b};font-weight:600"
                 translate="no">{pilot_b}</div>
        </div>""", unsafe_allow_html=True)

        for _, row in merged.iterrows():
            y      = int(row["year"])
            pts_a  = int(row[f"points_{pilot_a}"]) if pd.notna(row.get(f"points_{pilot_a}")) else "—"
            pts_b  = int(row[f"points_{pilot_b}"]) if pd.notna(row.get(f"points_{pilot_b}")) else "—"
            pos_a  = int(row[f"position_{pilot_a}"]) if pd.notna(row.get(f"position_{pilot_a}")) else "—"
            pos_b  = int(row[f"position_{pilot_b}"]) if pd.notna(row.get(f"position_{pilot_b}")) else "—"
            tm_a   = row.get(f"team_{pilot_a}", "—") if pd.notna(row.get(f"team_{pilot_a}")) else "—"
            tm_b   = row.get(f"team_{pilot_b}", "—") if pd.notna(row.get(f"team_{pilot_b}")) else "—"
            winner = pilot_a if (isinstance(pts_a, int) and isinstance(pts_b, int) and pts_a > pts_b) else \
                     pilot_b if (isinstance(pts_a, int) and isinstance(pts_b, int) and pts_b > pts_a) else "="

            bg = "#1A1F2E" if y % 2 == 0 else "#161B27"
            st.markdown(f"""
            <div style="background:{bg};border-radius:8px;padding:8px 12px;
                        margin-bottom:4px;display:grid;
                        grid-template-columns:60px 1fr 1fr;gap:8px;align-items:center">
                <div style="font-size:13px;font-weight:600;color:#F0C040">{y}</div>
                <div>
                    <div style="font-size:14px;font-weight:700;color:{'#FFD700' if winner==pilot_a else '#C8D8F0'}">{pts_a} pts</div>
                    <div style="font-size:9px;color:{clr_a}">P{pos_a} · {tm_a}</div>
                </div>
                <div>
                    <div style="font-size:14px;font-weight:700;color:{'#FFD700' if winner==pilot_b else '#C8D8F0'}">{pts_b} pts</div>
                    <div style="font-size:9px;color:{clr_b}">P{pos_b} · {tm_b}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
