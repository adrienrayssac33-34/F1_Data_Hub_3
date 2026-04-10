# pages/ml_page.py — F1 Data Hub · Prédictions IA
import sys, os as _os
_pages_dir = _os.path.dirname(_os.path.abspath(__file__))
_dash_dir  = _os.path.dirname(_pages_dir)
for _p in [_dash_dir, _pages_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from data_loader import get_laps, show_source_badge, TEAM_COLORS

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
    st.markdown(f"""
    <div class="page-header">
        <div class="page-icon">🤖</div>
        <div>
            <div class="page-title">Prédictions IA</div>
            <div class="page-sub">RandomForest · KMeans · Saison {year} · Manche {round_num:02d}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    show_source_badge(year=year, session_key=session_key)

    df = get_laps(session_key=session_key, year=year, round_num=round_num, n_laps=n_laps, circuit=circuit)

    if df.empty or "driver" not in df.columns:
        st.warning("Données indisponibles.")
        return

    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder
        from sklearn.cluster import KMeans
        from sklearn.metrics import accuracy_score
    except ImportError:
        st.error("scikit-learn non installé — `pip install scikit-learn`")
        return

    features = ["lap_number","lap_time_s","tyre_life"]
    if "sector1_s" in df.columns:
        features += ["sector1_s","sector2_s","sector3_s"]

    df_ml = df[features + ["compound","driver"]].dropna().copy()
    if len(df_ml) < 20:
        st.warning("Pas assez de données.")
        return

    le = LabelEncoder()
    df_ml["compound_enc"] = le.fit_transform(df_ml["compound"].astype(str))
    X = df_ml[features]
    y = df_ml["compound_enc"]
    np.random.seed(42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)
    rf      = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    acc_int = int(round(accuracy_score(y_test, rf.predict(X_test)) * 100))

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Précision",          f"{acc_int}%",      "RandomForest")
    with c2: st.metric("Train échantillons", str(len(X_train)),  "80% des données")
    with c3: st.metric("Test échantillons",  str(len(X_test)),   "20% des données")
    with c4: st.metric("Features",           str(len(features)), "variables entrée")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="data-card"><div class="card-title">Importance des features <span class="card-badge">RandomForest</span></div>', unsafe_allow_html=True)
        fi = pd.DataFrame({"feature":features,"importance":rf.feature_importances_}).sort_values("importance")
        fig = go.Figure(go.Bar(
            x=fi["importance"], y=fi["feature"], orientation="h",
            marker=dict(
                color=fi["importance"],
                colorscale=[[0,"#1E2535"],[0.5,"#4A8FE0"],[1.0,"#E10600"]],
            ),
            text=[f"{v:.3f}" for v in fi["importance"]],
            textposition="outside", textfont=dict(size=12, color="#FFFFFF"),
        ))
        fig.update_layout(**PLOT, height=320,
                          xaxis=dict(**AX, title="Importance"),
                          yaxis=dict(**AX_LIGHT),
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="data-card"><div class="card-title">Clustering KMeans <span class="card-badge">3 groupes</span></div>', unsafe_allow_html=True)
        km = KMeans(n_clusters=3, random_state=42, n_init=10)
        df_ml = df_ml.copy()
        df_ml["cluster"] = km.fit_predict(X).astype(str)
        fig2 = px.scatter(
            df_ml, x="lap_number", y="lap_time_s", color="cluster",
            color_discrete_sequence=["#E10600","#4A8FE0","#4AE8C0"],
            opacity=0.8,
            labels={"lap_number":"Tour","lap_time_s":"Temps (s)","cluster":"Cluster"},
        )
        fig2.update_traces(marker=dict(size=7))
        fig2.update_layout(**PLOT, height=320,
                           xaxis=dict(**AX, title="Tour"),
                           yaxis=dict(**AX, title="Temps (s)"),
                           legend=dict(bgcolor="#161B27", borderwidth=0.5,
                                       font=dict(color="#C8D4E8")))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="data-card"><div class="card-title">Compound réel par pilote <span class="card-badge">heatmap tours</span></div>', unsafe_allow_html=True)
    df_pred     = df_ml.copy()
    df_pred["compound_pred"] = le.inverse_transform(rf.predict(X))
    pivot       = df_pred.groupby(["driver","compound"])["lap_number"].count().reset_index()
    pivot_table = pivot.pivot(index="driver", columns="compound", values="lap_number").fillna(0)
    fig3 = go.Figure(go.Heatmap(
        z=pivot_table.values,
        x=list(pivot_table.columns),
        y=list(pivot_table.index),
        colorscale=[[0,"#0F1117"],[0.5,"#4A8FE0"],[1,"#E10600"]],
        text=pivot_table.values.astype(int),
        texttemplate="%{text}",
        textfont=dict(size=12, color="#E8EDF5"),
    ))
    fig3.update_layout(**PLOT, height=max(240, len(pivot_table)*40),
                       xaxis=dict(**AX_LIGHT),
                       yaxis=dict(**AX_LIGHT))
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
