#!/usr/bin/env python3
import pandas as pd
import numpy as np
import requests
from collections import Counter

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

def manual_label_flip(y, flip_frac=0.1, random_state=42):
    """
    Return a copy of y where `flip_frac` fraction of labels have been flipped.
    Works for binary (0/1) or multiclass.
    """
    y_flipped = y.copy()
    rng = np.random.RandomState(random_state)
    n = len(y_flipped)
    n_flip = int(flip_frac * n)
    idx = rng.choice(n, size=n_flip, replace=False)
    labels = np.unique(y_flipped)
    if len(labels) == 2:
        # Binary: flip 0<->1
        y_flipped[idx] = 1 - y_flipped[idx]
    else:
        # Multiclass: assign a different random label
        for i in idx:
            other = labels[labels != y_flipped[i]]
            y_flipped[i] = rng.choice(other)
    return y_flipped, idx

def main():
    # 1) Params
    FEATURES = [
        'src_bytes','dst_bytes','rerror_rate','dst_host_count',
        'dst_host_srv_count','dst_host_same_srv_rate',
        'dst_host_diff_srv_rate','dst_host_srv_diff_host_rate'
    ]
    TARGET   = 'labels'
    TRAIN_FP = 'processed_nsl_kdd_normal_malicious.csv'
    SERVER   = 'http://localhost:5000/correct_rules'

    # 2) Load & split
    df = pd.read_csv(TRAIN_FP)
    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # 3) Encode labels
    le = LabelEncoder()
    y_train_enc = le.fit_transform(y_train)
    y_test_enc  = le.transform(y_test)

    # 4) Train clean RF
    rf_clean = RandomForestClassifier(
        n_estimators=100, random_state=42, n_jobs=-1
    )
    rf_clean.fit(X_train, y_train_enc)
    acc_clean = accuracy_score(y_test_enc, rf_clean.predict(X_test))
    print(f"▶ Accuracy clean: {acc_clean:.4f}")

    # 5) Manual poisoning: flip 10% of labels
    flip_frac = 0.1
    y_train_p, flipped_idx = manual_label_flip(
        y_train_enc, flip_frac=flip_frac, random_state=42
    )
    print(f"▶ Manual poisoning: flipped {len(flipped_idx)} labels ({flip_frac*100:.0f}%)")

    # 6) Train poisoned RF
    rf_p = RandomForestClassifier(
        n_estimators=100, random_state=42, n_jobs=-1
    )
    rf_p.fit(X_train, y_train_p)
    acc_pois = accuracy_score(y_test_enc, rf_p.predict(X_test))
    print(f"▶ Accuracy poisoned: {acc_pois:.4f}  (drop {acc_pois - acc_clean:+.4f})")

    # 7) Extract “uncertain” rules
    all_rules = []
    for tree in rf_p.estimators_:
        txt = export_text(tree, feature_names=FEATURES)
        for line in txt.splitlines():
            if line.strip():
                all_rules.append(line.strip())
    threshold = len(rf_p.estimators_) * 0.5
    uncertain = [r for r,c in Counter(all_rules).items() if c < threshold]
    print(f"▶ Uncertain rules: {len(uncertain)}")

    # 8) Send to server & get corrections
    resp = requests.post(SERVER, json={'uncertain_rules': uncertain})
    corrected = resp.json().get('corrected_rules', [])
    print(f"▶ Corrected rules: {len(corrected)}")

    # 9) Re-weight samples for retraining
    weights = np.ones(len(y_train_p), dtype=float)
    for i, row in X_train.reset_index(drop=True).iterrows():
        for rule in corrected:
            cond = rule.split(" then")[0].replace("if ", "")
            try:
                if eval(cond, {}, row.to_dict()):
                    weights[i] *= 2.0
            except Exception:
                pass

    # 10) Retrain & evaluate final RF
    rf_final = RandomForestClassifier(
        n_estimators=200, max_depth=10,
        class_weight='balanced', random_state=42, n_jobs=-1
    )
    rf_final.fit(X_train, y_train_p, sample_weight=weights)
    acc_final = accuracy_score(y_test_enc, rf_final.predict(X_test))
    print(f"▶ Accuracy after correction: {acc_final:.4f}  (gain {acc_final - acc_pois:+.4f})")

if __name__ == "__main__":
    main()
