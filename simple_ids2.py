import pandas as pd
import joblib

# --- Configuration ---
FEATURE_COLUMNS = [
    'src_bytes', 'dst_bytes', 'rerror_rate', 'dst_host_count',
    'dst_host_srv_count', 'dst_host_same_srv_rate',
    'dst_host_diff_srv_rate', 'dst_host_srv_diff_host_rate'
]

UNLABELED_FILE = "output_features.csv"
MODEL_PATH = "corrected_rf_model.pkl"
ENCODER_PATH = "label_encoder.pkl"

# --- Load unlabeled feature data ---
def load_unlabeled_data(filepath):
    df = pd.read_csv(filepath)
    missing = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df[FEATURE_COLUMNS]

def main():
    print("[*] Loading trained model...")
    model = joblib.load(MODEL_PATH)

    print("[*] Loading label encoder...")
    label_encoder = joblib.load(ENCODER_PATH)

    print("[*] Loading unlabeled feature data...")
    X_unlabeled = load_unlabeled_data(UNLABELED_FILE)

    print("[*] Predicting...")
    predictions = model.predict(X_unlabeled)
    decoded_predictions = label_encoder.inverse_transform(predictions)

    print("\n=== Prediction Results ===")
    for i, label in enumerate(decoded_predictions):
        print(f"Sample {i+1}: {label}")

if __name__ == "__main__":
    main()
