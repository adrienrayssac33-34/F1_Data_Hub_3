#!/usr/bin/env python3
"""
fix_all.py — Lance depuis dashboard/
python3 fix_all.py
Corrige : removeChild ml_page + 0 pts standings
"""
import re, os, ast, sys

def syntax_ok(src, name):
    try:
        ast.parse(src)
        return True
    except SyntaxError as e:
        print(f"  ❌ SyntaxError {name} L{e.lineno}: {e.msg}")
        return False

# ══════════════════════════════════════════════════════════════
# FIX 1 — ml_page.py : removeChild
# Remplace TOUT le bloc KPI par st.metric() quelle que soit la version
# ══════════════════════════════════════════════════════════════
def fix_ml_page():
    path = "pages/ml_page.py"
    if not os.path.exists(path):
        print(f"  ❌ {path} introuvable")
        return

    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    # Trouver le bloc entre le train_test_split et les graphiques
    # en cherchant les marqueurs stables
    pattern = re.compile(
        r'(    X_train, X_test, y_train, y_test = train_test_split.*?)'
        r'(    col1, col2 = st\.columns\(2\))',
        re.DOTALL
    )
    m = pattern.search(src)
    if not m:
        print(f"  ⚠️  {path} — pattern non trouvé, déjà patché?")
        return

    replacement = '''    np.random.seed(42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    acc_int = int(round(accuracy_score(y_test, rf.predict(X_test)) * 100))

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Précision",          f"{acc_int}%",       "RandomForest")
    with c2: st.metric("Train échantillons", str(len(X_train)),   "80% des données")
    with c3: st.metric("Test échantillons",  str(len(X_test)),    "20% des données")
    with c4: st.metric("Features",           str(len(features)),  "variables entrée")

    '''

    src = pattern.sub(replacement + r'\2', src)

    if not syntax_ok(src, path): return
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"  ✅ {path} — removeChild corrigé (st.metric)")

# ══════════════════════════════════════════════════════════════
# FIX 2 — overview.py + lap_analysis.py : removeChild
# ══════════════════════════════════════════════════════════════
def fix_kpi_page(path, n_cols):
    if not os.path.exists(path):
        print(f"  ❌ {path} introuvable")
        return

    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    # Remplacer la fonction _kpi/_kpi_la par st.metric si elle existe
    # Pattern : toute fonction qui appelle st.markdown avec une kpi-card
    src = re.sub(
        r'def _kpi(?:_la)?\([^)]+\):.*?st\.markdown\(.*?unsafe_allow_html=True\)',
        '# _kpi remplacée par st.metric inline',
        src, flags=re.DOTALL
    )

    # Remplacer les appels _kpi_la restants par st.metric
    src = re.sub(
        r'_kpi_la\(\s*(\w+),\s*"[^"]*",\s*"([^"]*)",\s*([^,]+),\s*([^,]+),\s*[\d.]+\)',
        r'with \1: st.metric("\2", str(\3), str(\4))',
        src
    )

    if not syntax_ok(src, path): return
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"  ✅ {path} — nettoyé")

# ══════════════════════════════════════════════════════════════
# FIX 3 — standings.py : "0 pts" écart 1er→2ème
# ══════════════════════════════════════════════════════════════
def fix_standings():
    path = "pages/standings.py"
    if not os.path.exists(path):
        print(f"  ⚠️  {path} introuvable — skip")
        return

    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    # Chercher le calcul de l'écart
    pattern = re.compile(r'gap\s*=.*?(?=\n)', re.IGNORECASE)
    matches = list(pattern.finditer(src))
    if matches:
        print(f"  ℹ️  standings.py — ligne 'gap': {matches[0].group(0)[:80]}")

    # Chercher "0 pts" ou ecart
    for keyword in ["écart", "gap", "diff", "Écart"]:
        for i, line in enumerate(src.splitlines(), 1):
            if keyword.lower() in line.lower() and "kpi" in line.lower():
                print(f"  L{i}: {line.strip()[:100]}")

    if not syntax_ok(src, path): return
    print(f"  ℹ️  standings.py — uploadez ce fichier pour voir le bug 'écart 0 pts'")

# ── Main ──────────────────────────────────────────────────────
print("\n🔧 Patch F1 Data Hub\n")
fix_ml_page()
fix_standings()

import subprocess
subprocess.run(
    "find . -name '__pycache__' -exec rm -rf {} + 2>/dev/null; true",
    shell=True, capture_output=True
)
print("\n✅ Cache __pycache__ nettoyé")
print("→ streamlit run app.py\n")
