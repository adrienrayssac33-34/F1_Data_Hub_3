"""
fix_dataloader.py
=================
Lance ce script UNE SEULE FOIS depuis le dossier dashboard/ :

    python3 fix_dataloader.py

Il patche data_loader.py directement sur ton disque.
"""
import re, sys, os

target = "data_loader.py"

if not os.path.exists(target):
    print(f"ERREUR : {target} introuvable.")
    print(f"Lance ce script depuis le dossier dashboard/ (là où se trouve data_loader.py)")
    sys.exit(1)

with open(target, "r", encoding="utf-8") as f:
    src = f.read()

original = src

# ── Fix 1 : supprimer @st.cache_data juste avant def get_weather ──────────
src = re.sub(
    r'@st\.cache_data\([^)]*\)\s*\n(?=def get_weather\()',
    '',
    src
)

# ── Fix 2 : remplacer tout le corps de _load_fastf1_weather par stub vide ─
# On cherche la fonction et on remplace jusqu'à la prochaine def/décorateur
src = re.sub(
    r'(@st\.cache_data\([^)]*\)\s*\n)?def _load_fastf1_weather\(year: int, round_num: int\).*?(?=\n\n\n|\n@st\.cache_data|\ndef [a-z_A-Z]|\nREQUIRED|\n# ══)',
    (
        'def _load_fastf1_weather(year: int, round_num: int):\n'
        '    """FastF1 weather désactivé — NameError interne irrécupérable."""\n'
        '    import pandas as _pd\n'
        '    return _pd.DataFrame()'
    ),
    src,
    flags=re.DOTALL
)

if src == original:
    print("⚠️  Aucune modification effectuée — le fichier est peut-être déjà patché.")
    print("   Vérifie avec : grep -n 'def get_weather\\|cache_data' data_loader.py")
    sys.exit(0)

# Sauvegarde
with open(target + ".bak", "w", encoding="utf-8") as f:
    f.write(original)

with open(target, "w", encoding="utf-8") as f:
    f.write(src)

# Vérification
lines = src.splitlines()
print("\n✅ data_loader.py patché. Vérification :")
for i, l in enumerate(lines, 1):
    if 'def get_weather' in l or 'def _load_fastf1_weather' in l:
        prev = lines[i-2] if i >= 2 else ""
        decorated = "@st.cache_data" in prev
        status = "❌ encore décoré!" if decorated else "✅ sans cache_data"
        print(f"  L{i}: {l.strip()}  →  {status}")

print("\n👉 Lance maintenant :")
print("   find . -name '__pycache__' -exec rm -rf {} + 2>/dev/null")
print("   streamlit run app.py")
