#!/usr/bin/env python3
"""
patch_kpi.py — Lance depuis dashboard/
python3 patch_kpi.py
"""
import re, os, ast, sys

PAGES = [
    "pages/ml_page.py",
    "pages/overview.py", 
    "pages/lap_analysis.py",
    "pages/telemetry.py",
    "pages/strategy.py",
    "pages/weather.py",
]

def check_syntax(src, fname):
    try:
        ast.parse(src)
        return True
    except SyntaxError as e:
        print(f"  ❌ SyntaxError dans {fname}: {e}")
        return False

# ─── ml_page.py ───────────────────────────────────────────────
def patch_ml_page(src):
    old = '''    le = LabelEncoder()
    df_ml["compound_enc"] = le.fit_transform(df_ml["compound"].astype(str))
    X = df_ml[features]
    y = df_ml["compound_enc"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf  = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    acc = accuracy_score(y_test, rf.predict(X_test))

    # Pré-calcul des valeurs — évite les f-strings imbriquées
    acc_pct    = f"{acc*100:.1f}%"
    acc_pct_w  = str(int(acc*100))
    n_train    = str(len(X_train))
    n_test     = str(len(X_test))
    n_feat     = str(len(features))

    def _kpi_ml(col, accent, label, value, sub, pct):
        html = (
            '<div class="kpi-card">'
            '<div class="kpi-accent" style="background:' + accent + '"></div>'
            '<div class="kpi-label">' + label + '</div>'
            '<div class="kpi-value">' + value + '</div>'
            '<div class="kpi-sub">' + sub + '</div>'
            '<div class="kpi-bar"><div class="kpi-bar-fill" '
            'style="width:' + str(pct) + '%;background:' + accent + '"></div></div>'
            '</div>'
        )
        with col:
            st.markdown(html, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    _kpi_ml(c1, "#E10600", "Precision",         acc_pct,  "RandomForest",      acc_pct_w)
    _kpi_ml(c2, "#4A8FE0", "Train echantillons", n_train, "80% des donnees",   80)
    _kpi_ml(c3, "#FF8000", "Test echantillons",  n_test,  "20% des donnees",   20)
    _kpi_ml(c4, "#9A7FDD", "Features",           n_feat,  "variables entree",  100)'''

    new = '''    np.random.seed(42)
    le = LabelEncoder()
    df_ml["compound_enc"] = le.fit_transform(df_ml["compound"].astype(str))
    X  = df_ml[features]
    y  = df_ml["compound_enc"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    acc_int = int(round(accuracy_score(y_test, rf.predict(X_test)) * 100))

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Précision",          f"{acc_int}%",      "RandomForest")
    with c2: st.metric("Train échantillons", str(len(X_train)),  "80% des données")
    with c3: st.metric("Test échantillons",  str(len(X_test)),   "20% des données")
    with c4: st.metric("Features",           str(len(features)), "variables entrée")'''

    if old in src:
        return src.replace(old, new), True
    return src, False

# ─── overview.py ──────────────────────────────────────────────
def patch_overview(src):
    # Remplacer la fonction _kpi par st.metric
    old_fn = '''def _kpi(label, value, sub, color, pct=100):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-accent" style="background:{color}"></div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" translate="no">{value}</div>
        <div class="kpi-sub">{sub}</div>
        <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{pct}%;background:{color}"></div></div>
    </div>""", unsafe_allow_html=True)'''
    new_fn = '''def _kpi(label, value, sub, color, pct=100):
    st.metric(label=label, value=str(value), delta=str(sub) if sub else None)'''

    if old_fn not in src:
        return src, False
    src = src.replace(old_fn, new_fn)

    # Nettoyer les appels avec paramètres color/pct inutiles
    old_kpi_block = '''    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: _kpi(f"Champion {year}", champion,    f"{champ_pts} pts",            "#E10600", 100)
    with c2: _kpi("Meilleur tour",    fastest_drv, lap_str,                        "#4A8FE0", 100)
    with c3: _kpi("Tours analysés",   str(len(df_laps)),
                  f"{n_laps} t. · {n_drivers} pilotes", "#FF8000",
                  min(100, round(len(df_laps) / max(1, n_laps * n_drivers) * 100)))
    with c4: _kpi("Pit stops",        str(len(df_pit)),
                  f"moy. {avg_pit:.2f}s",          "#4AE8C0", min(100, len(df_pit) * 5))
    with c5: _kpi("Équipes",          str(n_teams), "en course", "#9A7FDD", n_teams * 20)'''

    new_kpi_block = '''    _valid      = df_laps[df_laps["lap_time_s"].notna() & (df_laps["lap_time_s"] > 0)]
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

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric(f"Champion {year}", champion,    f"{champ_pts} pts")
    with c2: st.metric("Meilleur tour",    fastest_drv, lap_str)
    with c3: st.metric("Tours analysés",   str(len(df_laps)), f"{n_laps} t. · {n_drivers} pilotes")
    with c4: st.metric("Pit stops",        str(len(df_pit)),  f"moy. {avg_pit:.2f}s")
    with c5: st.metric("Équipes",          str(n_teams),      "en course")'''

    # Retirer aussi les calculs dupliqués avant ce bloc
    src = re.sub(
        r'    # ── KPIs ─+\n    fastest_idx = .*?(?=\n    c1, c2, c3, c4, c5)',
        '    # ── KPIs ─────────────────────────────────────────────────',
        src, flags=re.DOTALL
    )
    if old_kpi_block in src:
        src = src.replace(old_kpi_block, new_kpi_block)
    return src, True

# ─── lap_analysis.py ──────────────────────────────────────────
def patch_lap_analysis(src):
    old = '''    # ── KPIs ──────────────────────────────────────────────────
    best_row   = df.loc[df["lap_time_s"].idxmin()]
    mins, secs = divmod(best_row["lap_time_s"], 60)
    c1, c2, c3, c4 = st.columns(4)
    def _kpi_la(col, accent, label, value, sub, pct):
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

    best_drv  = str(best_row["driver"])
    lap_str   = f"{int(mins)}:{secs:06.3f}"
    avg_str   = f"{df['lap_time_s'].mean():.3f}s"
    std_str   = f"s={df['lap_time_s'].std():.3f}"
    _cpd      = df["compound"].mode()[0] if "compound" in df.columns else "—"
    _cpd_clr  = {"SOFT":"#E8002D","MEDIUM":"#FFD700","HARD":"#D0D0D0",
                 "INTERMEDIATE":"#39B54A","WET":"#0093CC"}.get(_cpd, "#9A7FDD")

    _kpi_la(c1, "#E10600", "Meilleur tour",     best_drv,       lap_str,                           100)
    _kpi_la(c2, "#4A8FE0", "Temps moyen",       avg_str,        std_str,                           80)
    _kpi_la(c3, "#FF8000", "Tours filtres",      str(len(df)),  str(len(sel_drivers)) + " pilotes", 70)
    _kpi_la(c4, _cpd_clr,  "Compound dominant", _cpd,           "pneu majoritaire",                90)'''

    new = '''    # ── KPIs ──────────────────────────────────────────────────
    _valid    = df[df["lap_time_s"].notna() & (df["lap_time_s"] > 0)]
    if _valid.empty: _valid = df
    best_row  = _valid.loc[_valid["lap_time_s"].idxmin()]
    mins, secs = divmod(float(best_row["lap_time_s"]), 60)
    best_drv  = str(best_row["driver"])
    lap_str   = f"{int(mins)}:{secs:06.3f}"
    avg_str   = f"{float(df['lap_time_s'].mean()):.3f}s"
    std_str   = f"±{float(df['lap_time_s'].std()):.3f}s"
    _cpd      = str(df["compound"].mode()[0]) if "compound" in df.columns and len(df) else "—"

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Meilleur tour",     best_drv,       lap_str)
    with c2: st.metric("Temps moyen",       avg_str,        std_str)
    with c3: st.metric("Tours analysés",    str(len(df)),   str(len(sel_drivers)) + " pilotes")
    with c4: st.metric("Compound dominant", _cpd,           "pneu majoritaire")'''

    if old in src:
        return src.replace(old, new), True
    return src, False

# ─── Main ─────────────────────────────────────────────────────
import sys
errors = 0
for page_path in PAGES:
    if not os.path.exists(page_path):
        print(f"  ⏭  {page_path} absent — ignoré")
        continue
    with open(page_path, "r", encoding="utf-8") as f:
        src = f.read()

    patched = False
    if "ml_page" in page_path:
        src, patched = patch_ml_page(src)
    elif "overview" in page_path:
        src, patched = patch_overview(src)
    elif "lap_analysis" in page_path:
        src, patched = patch_lap_analysis(src)
    else:
        print(f"  ⏭  {page_path} — pas de patch défini")
        continue

    if not patched:
        print(f"  ⚠️  {page_path} — pattern non trouvé (déjà patché?)")
        continue

    if not check_syntax(src, page_path):
        errors += 1
        continue

    with open(page_path, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"  ✅ {page_path} patché")

import subprocess
subprocess.run(["find", ".", "-name", "__pycache__", "-exec", "rm", "-rf", "{}", "+"],
               capture_output=True)
print("\n✅ Cache __pycache__ nettoyé")
print(f"\n{'✅ Terminé' if errors == 0 else f'❌ {errors} erreur(s)'}")
print("\nRelance: streamlit run app.py")
