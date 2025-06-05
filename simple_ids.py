import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Define the only features to use
FEATURE_COLUMNS = [
    'src_bytes', 'dst_bytes', 'rerror_rate', 'dst_host_count',
    'dst_host_srv_count', 'dst_host_same_srv_rate',
    'dst_host_diff_srv_rate', 'dst_host_srv_diff_host_rate'
]



# File paths
NSLKDD_FILE = "kdd_processed.csv"             # Your labeled dataset
UNLABELED_FILE = "output_features.csv"  # Extracted features to classify

def load_nslkdd_dataset(filepath):
    df = pd.read_csv(filepath)

    # Check if label exists
    if 'labels' not in df.columns:
        raise ValueError("Missing 'label' column in NSL-KDD dataset")

    # Keep only the selected features and the label
    missing = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"NSL-KDD dataset is missing columns: {missing}")

    X = df[FEATURE_COLUMNS]
    y = df['labels']

    # Encode label
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    return X, y_encoded, label_encoder

def train_model(X, y):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def load_unlabeled_data(filepath):
    df = pd.read_csv(filepath)

    # Ensure the unlabeled data has only the expected features
    missing = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Unlabeled dataset is missing columns: {missing}")

    return df[FEATURE_COLUMNS]

def main():
    print("[*] Loading and training on NSL-KDD dataset...")
    X_train, y_train, label_encoder = load_nslkdd_dataset(NSLKDD_FILE)

    print("[*] Training Random Forest model...")
    model = train_model(X_train, y_train)

    print("[*] Loading unlabeled data from output_features.csv...")
    X_unlabeled = load_unlabeled_data(UNLABELED_FILE)

    print("[*] Predicting labels...")
    predictions = model.predict(X_unlabeled)
    decoded = label_encoder.inverse_transform(predictions)

    print("\n=== Prediction Results ===")
    for i, label in enumerate(decoded):
        print(f"Sample {i+1}: {label}")

if __name__ == "__main__":
    main()
