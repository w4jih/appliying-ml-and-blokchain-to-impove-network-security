import pandas as pd
from collections import Counter
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import export_text
from sklearn.model_selection import train_test_split

# 1) Paramètres
FEATURE_COLUMNS = [
    'src_bytes', 'dst_bytes', 'rerror_rate', 'dst_host_count',
    'dst_host_srv_count', 'dst_host_same_srv_rate',
    'dst_host_diff_srv_rate', 'dst_host_srv_diff_host_rate'
]
TARGET_COLUMN = 'labels'
TRAIN_PATH = 'processed-kdd2.csv'  # Remplacez par le chemin de votre CSV
OUTPUT_RULES_FILE = 'certain_rules.txt'

# 2) Charger les données
df = pd.read_csv(TRAIN_PATH)
X = df[FEATURE_COLUMNS]
y = df[TARGET_COLUMN]

# 3) Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 4) Entraîner le RandomForestClassifier
rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

# 5) Extraire les règles de chaque arbre au format texte
n_trees = len(rf.estimators_)
rule_tree_count = Counter()

for tree in rf.estimators_:
    # export_text renvoie une chaîne où chaque ligne correspond à un noeud/règle
    txt = export_text(tree, feature_names=FEATURE_COLUMNS)
    # On récupère chaque ligne non vide (strip pour enlever indentation ASCII-art)
    lines = [line.strip() for line in txt.splitlines() if line.strip()]
    # Pour que chaque règle ne soit comptée qu'une fois par arbre, on prend l'ensemble
    unique_lines = set(lines)
    for rule in unique_lines:
        rule_tree_count[rule] += 1

# 5.a) Afficher le nombre total de règles uniques extraites
total_unique_rules = len(rule_tree_count)
print(f"Nombre total de règles uniques extraites des {n_trees} arbres : {total_unique_rules}")

# 6) Sélectionner les "certain rules" : celles présentes dans > 50% des arbres
threshold = n_trees * 0.5
certain_rules = [
    rule for rule, count in rule_tree_count.items()
    if count > threshold
]

# 6.a) Afficher le nombre de "certain rules"
num_certain = len(certain_rules)
print(f"Nombre de règles ‘certaines’ (apparaissent dans >50% des arbres) : {num_certain}")

# 7) Sauvegarder ces règles dans un fichier texte
with open(OUTPUT_RULES_FILE, 'w') as f:
    for rule in certain_rules:
        f.write(rule + '\n')

print(f"{num_certain} règles sauvegardées dans '{OUTPUT_RULES_FILE}'.")
