import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Define the feature columns to use for training
FEATURE_COLUMNS = [
    'src_bytes', 'dst_bytes', 'count', 'rerror_rate', 'dst_host_count',
    'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_rerror_rate'
]

# Load the processed dataset
processed_data = pd.read_csv('~/Desktop/pfa/NSL-KDD-Network-Intrusion-Detection/processed_nsl_kdd_normal_malicious.csv')

# Extract features and labels
X = processed_data[FEATURE_COLUMNS]
y = processed_data['labels']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Evaluate the model on the test set
y_pred = model.predict(X_test)
print("Classification Report on Test Set:")
print(classification_report(y_test, y_pred))

# Load the extracted_features.csv file
extracted_features = pd.read_csv('~/Desktop/pfa/NSL-KDD-Network-Intrusion-Detection/extracted_features.csv')

# Ensure the extracted features have the same columns as the training data
if set(FEATURE_COLUMNS).issubset(extracted_features.columns):
    X_extracted = extracted_features[FEATURE_COLUMNS]
    
    # Predict labels for the extracted features
    predictions = model.predict(X_extracted)
    
    # Print the predictions to the terminal
    print("Predictions for extracted_features.csv:")
    for i, pred in enumerate(predictions):
        print(f"Row {i + 1}: {pred}")
else:
    print("Error: The extracted_features.csv file does not contain the required feature columns.")