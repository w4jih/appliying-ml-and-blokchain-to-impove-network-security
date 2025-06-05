
import pandas as pd
import requests
from collections import Counter
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 1) Paramètres
FEATURE_COLUMNS = [
    'src_bytes', 'dst_bytes', 'rerror_rate', 'dst_host_count',
    'dst_host_srv_count', 'dst_host_same_srv_rate',
    'dst_host_diff_srv_rate', 'dst_host_srv_diff_host_rate'
]
TARGET_COLUMN = 'labels'      # or 'attack'
TRAIN_PATH    = 'processed_nsl_kdd_normal_malicious.csv'
SERVER_URL    = 'http://0.0.0.0:5000/correct_rules'  # match Flask server

# 2) Chargement & split
df = pd.read_csv(TRAIN_PATH)
X = df[FEATURE_COLUMNS]
y = df[TARGET_COLUMN]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 3) Entraînement initial
rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
acc_before = accuracy_score(y_test, y_pred)
print(f"Accuracy avant correction : {acc_before:.4f}")

# 4) Extraction des règles incertaines
all_rules = []
for tree in rf.estimators_:
    txt = export_text(tree, feature_names=FEATURE_COLUMNS)
    for line in txt.split('\n'):
        l = line.strip()
        if l:
            all_rules.append(l)

rule_counts = Counter(all_rules)
threshold = len(rf.estimators_) * 0.5
uncertain_rules = [r for r, cnt in rule_counts.items() if cnt < threshold]
print(f"Règles incertaines extraites : {len(uncertain_rules)}")

# 5) Envoi au serveur pour correction (accumulé sur serveur)
resp = requests.post(SERVER_URL, json={'uncertain_rules': uncertain_rules})
all_corrected_rules = resp.json().get('all_corrected_rules', [])
print(f"Règles corrigées globales reçues du serveur : {len(all_corrected_rules)}")

# 6) Création de poids d’échantillons basés sur les règles corrigées
weights = [1.0] * len(y_train)
for idx, row in X_train.iterrows():
    for rule in all_corrected_rules:
        cond = rule.split(" then")[0].replace("if ", "")
        try:
            if eval(cond, {}, row.to_dict()):
                weights[idx] *= 1.5
        except Exception:
            pass

# 7) Ré-entraînement avec les poids & évaluation
rf2 = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
rf2.fit(X_train, y_train, sample_weight=weights)
y_pred2 = rf2.predict(X_test)
acc_after = accuracy_score(y_test, y_pred2)
print(f"Accuracy après correction : {acc_after:.4f}")
print(f"Amélioration : {acc_after - acc_before:+.4f}")

