import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

# Define the features used in your feature extraction code
FEATURE_COLUMNS = [
    'src_bytes', 'dst_bytes', 'count', 'rerror_rate', 'dst_host_count',
    'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_rerror_rate'
]

# Step 1: Load and preprocess the processed_nsl_kdd dataset
def load_and_preprocess_nsl_kdd(filepath):
    # Load the dataset
    df = pd.read_csv(filepath)
    
    # Filter only the features used in your feature extraction code
    X = df[FEATURE_COLUMNS]  # Features
    y = df.iloc[:, -1]       # Labels (assuming the last column is the label)
    
    # Encode labels (if they are strings)
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)
    
    return X, y, label_encoder

# Step 2: Train a machine learning model
def train_model(X_train, y_train):
    # Use SMOTE to oversample minority classes
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    
    # Define the parameter grid for hyperparameter tuning
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'class_weight': ['balanced', None]
    }
    
    # Perform grid search
    model = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, scoring='accuracy', n_jobs=-1)
    grid_search.fit(X_train_res, y_train_res)
    
    # Get the best model
    best_model = grid_search.best_estimator_
    print("Best Parameters: ", grid_search.best_params_)
    return best_model

# Step 3: Load the extracted_features.csv
def load_extracted_features(filepath):
    df = pd.read_csv(filepath)
    return df

# Step 4: Predict using the trained model
def predict_and_label(model, X_test, label_encoder):
    predictions = model.predict(X_test)
    labels = label_encoder.inverse_transform(predictions)
    return labels

# Step 5: Output the predictions
def print_predictions(labels):
    for i, label in enumerate(labels):
        print(f"Flow {i+1}: {'Malicious' if label == 1 else 'Benign'}")

# Main function
def main():
    # Paths to the datasets
    nsl_kdd_path = '~/Desktop/pfa/NSL-KDD-Network-Intrusion-Detection/processed_nsl_kdd.csv'  # Update this path
    extracted_features_path = '~/Desktop/pfa/NSL-KDD-Network-Intrusion-Detection/extracted_features.csv'
    
    # Load and preprocess the NSL-KDD dataset
    X, y, label_encoder = load_and_preprocess_nsl_kdd(nsl_kdd_path)
    
    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train the model
    model = train_model(X_train, y_train)
    
    # Evaluate the model on the test set (optional)
    y_pred = model.predict(X_test)
    print("Model Evaluation on NSL-KDD Test Set:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    
    # Load the extracted features
    extracted_features = load_extracted_features(extracted_features_path)
    
    # Ensure the extracted features have the same columns as the training data
    extracted_features = extracted_features[FEATURE_COLUMNS]
    
    # Predict and label the extracted features
    labels = predict_and_label(model, extracted_features, label_encoder)
    
    # Print the predictions
    print("\nPredictions for Extracted Features:")
    print_predictions(labels)
    
    
    #--
"""import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

# Define the features used in your feature extraction code
FEATURE_COLUMNS = [
    'src_bytes', 'dst_bytes', 'count', 'rerror_rate', 'dst_host_count',
    'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_rerror_rate'
]

# Step 1: Load and preprocess the processed_nsl_kdd dataset
def load_and_preprocess_nsl_kdd(filepath):
    # Load the dataset
    df = pd.read_csv(filepath)
    
    # Filter only the features used in your feature extraction code
    X = df[FEATURE_COLUMNS]  # Features
    y = df.iloc[:, -1]       # Labels (assuming the last column is the label)
    
    # Encode labels (if they are strings)
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)
    
    return X, y, label_encoder

# Step 2: Train a machine learning model
def train_model(X_train, y_train):
    # Use SMOTE to oversample minority classes
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    
    # Define the parameter distribution for randomized search
    param_dist = {
        'n_estimators': [50, 100],  # Fewer values
        'max_depth': [10, 20],      # Fewer values
        'min_samples_split': [2, 5], # Fewer values
        'min_samples_leaf': [1, 2],  # Fewer values
        'class_weight': ['balanced'] # Only one value
    }
    
    # Perform randomized search
    model = RandomForestClassifier(random_state=42)
    random_search = RandomizedSearchCV(estimator=model, param_distributions=param_dist, n_iter=10, cv=3, scoring='accuracy', n_jobs=-1, random_state=42)
    random_search.fit(X_train_res, y_train_res)
    
    # Get the best model
    best_model = random_search.best_estimator_
    print("Best Parameters: ", random_search.best_params_)
    return best_model

# Step 3: Load the extracted_features.csv
def load_extracted_features(filepath):
    df = pd.read_csv(filepath)
    return df

# Step 4: Predict using the trained model
def predict_and_label(model, X_test, label_encoder):
    predictions = model.predict(X_test)
    labels = label_encoder.inverse_transform(predictions)
    return labels

# Step 5: Output the predictions
def print_predictions(labels):
    for i, label in enumerate(labels):
        print(f"Flow {i+1}: {'Malicious' if label == 1 else 'Benign'}")

# Main function
def main():
    # Paths to the datasets
    nsl_kdd_path = 'processed_nsl_kdd.csv'  # Update this path
    extracted_features_path = 'extracted_features.csv'
    
    # Load and preprocess the NSL-KDD dataset
    X, y, label_encoder = load_and_preprocess_nsl_kdd(nsl_kdd_path)
    
    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train the model
    model = train_model(X_train, y_train)
    
    # Evaluate the model on the test set (optional)
    y_pred = model.predict(X_test)
    print("Model Evaluation on NSL-KDD Test Set:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    
    # Load the extracted features
    extracted_features = load_extracted_features(extracted_features_path)
    
    # Ensure the extracted features have the same columns as the training data
    extracted_features = extracted_features[FEATURE_COLUMNS]
    
    # Predict and label the extracted features
    labels = predict_and_label(model, extracted_features, label_encoder)
    
    # Print the predictions
    print("\nPredictions for Extracted Features:")
    print_predictions(labels)

if __name__ == '__main__':
    main()
   """ 

if __name__ == '__main__':
    main()