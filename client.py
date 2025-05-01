# client_app.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import export_text
from sklearn.model_selection import train_test_split
from joblib import dump
import requests
import os

class RuleExtractorClient:
    def __init__(self, config):
        self.feature_columns = config['FEATURE_COLUMNS']
        self.target_column = config['TARGET_COLUMN']
        self.data_path = config['DATA_PATH']
        self.server_url = config['SERVER_URL']
        
    def load_data(self):
        print("Chargement des données...")
        df = pd.read_csv(self.data_path)
        missing_cols = [col for col in self.feature_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Colonnes manquantes: {missing_cols}")
        return df

    def train_model(self, df):
        X = df[self.feature_columns]
        y = df[self.target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        print("Entraînement du Random Forest...")
        rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42,
            class_weight='balanced'
        )
        rf.fit(X_train, y_train)
        
        print(f"Score sur l'ensemble de test: {rf.score(X_test, y_test):.4f}")
        return rf

    def extract_rules(self, model):
        print("Extraction des règles...")
        rules = []
        for i, tree in enumerate(model.estimators_):
            tree_rules = export_text(
                tree,
                feature_names=self.feature_columns,
                spacing=2,
                decimals=2
            )
            rules.append({'tree_index': i, 'rules': tree_rules})
        return rules

    def send_to_server(self, rules):
        print("Envoi des règles au serveur...")
        dump(rules, 'temp_rules.joblib')
        
        with open('temp_rules.joblib', 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.server_url}/upload_rules",
                files=files
            )
        
        os.remove('temp_rules.joblib')
        return response.json()

if __name__ == "__main__":
    config = {
        'FEATURE_COLUMNS': [
            'src_bytes', 'dst_bytes', 'rerror_rate', 'dst_host_count',
            'dst_host_srv_count', 'dst_host_same_srv_rate', 
            'dst_host_diff_srv_rate', 'dst_host_srv_diff_host_rate'
        ],
        'TARGET_COLUMN': 'labels',
        'DATA_PATH': 'processed_nsl_kdd_normal_malicious.csv',
        'SERVER_URL': 'http://localhost:5000'
    }
    
    client = RuleExtractorClient(config)
    try:
        df = client.load_data()
        model = client.train_model(df)
        rules = client.extract_rules(model)
        server_response = client.send_to_server(rules)
        print("Réponse du serveur:", server_response)
    except Exception as e:
        print("Erreur:", str(e))