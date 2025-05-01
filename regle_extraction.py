
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from collections import defaultdict
from sklearn.tree import _tree
import pandas as pd
from joblib import dump
import warnings
from sklearn.model_selection import train_test_split

def improved_rule_extraction(rf_model, X_train, y_train, feature_names, min_samples_leaf=10, accuracy_threshold=0.85):
    
    rule_data = []
    
    for tree_idx, tree in enumerate(rf_model.estimators_):
        tree_ = tree.tree_
        
        # Get true feature indices used in the tree
        feature_idx = [i for i in tree_.feature if i != _tree.TREE_UNDEFINED]
        
        # Verify feature names match
        if len(feature_names) <= max(feature_idx):
            raise ValueError("Feature names don't match tree structure")
            
        for leaf_id in np.where(tree_.children_left == _tree.TREE_LEAF)[0]:
            node_indicator = tree.decision_path(X_train)
            leaf_samples = node_indicator[:, leaf_id].nonzero()[0]
            
            if len(leaf_samples) < min_samples_leaf:
                continue
                
            y_leaf = y_train.iloc[leaf_samples]
            pred_class = tree_.value[leaf_id].argmax()
            accuracy = (y_leaf == pred_class).mean()
            
            if accuracy >= accuracy_threshold:
                rule = extract_rule_from_path(tree, leaf_id, feature_names)
                
                # Skip empty/invalid rules
                if rule and "AND" in rule:  
                    rule_data.append({
                        'tree': tree_idx,
                        'leaf_id': leaf_id,
                        'rule': rule,
                        'class': pred_class,
                        'accuracy': accuracy,
                        'support': len(leaf_samples)
                    })
    
    return pd.DataFrame(rule_data)

def extract_rule_from_path(tree, leaf_id, feature_names):
    
    tree_ = tree.tree_
    node_path = []
    current = leaf_id
    
    # Walk up to root
    while current != 0:
        parent = np.where(tree_.children_left == current)[0]
        if len(parent) == 0:
            parent = np.where(tree_.children_right == current)[0]
        if len(parent) == 0:
            break
        node_path.append(parent[0])
        current = parent[0]
    
    # Build conditions
    conditions = []
    for node in reversed(node_path):
        feat_idx = tree_.feature[node]
        if feat_idx == _tree.TREE_UNDEFINED:
            continue
            
        threshold = tree_.threshold[node]
        feat_name = feature_names[feat_idx]
        
        if tree_.children_left[node] in node_path:
            conditions.append(f"{feat_name} <= {threshold:.4f}")
        else:
            conditions.append(f"{feat_name} > {threshold:.4f}")
    
    return " AND ".join(conditions) if conditions else None

def eval_rule(rule, X):
    
    if not rule or pd.isna(rule):
        return np.zeros(len(X), dtype=bool)
        
    mask = np.ones(len(X), dtype=bool)
    try:
        for condition in rule.split(" AND "):
            parts = condition.strip().split()
            if len(parts) != 3:
                continue
                
            var, op, val = parts
            col = X[var]
            
            if op == "<=":
                mask &= (col <= float(val))
            elif op == ">":
                mask &= (col > float(val))
    except:
        return np.zeros(len(X), dtype=bool)
        
    return mask

# Main execution
if __name__ == "__main__":
    # Load your specific dataset
    data = pd.read_csv("processed_nsl_kdd_normal_malicious.csv")
    
    # Select specific features
    FEATURE_COLUMNS = [
        'src_bytes', 
        'dst_bytes', 
        'rerror_rate',
        'dst_host_count',
        'dst_host_srv_count', 
        'dst_host_same_srv_rate',
        'dst_host_diff_srv_rate',
        'dst_host_srv_diff_host_rate'
    ]
    
    X = data[FEATURE_COLUMNS]
    y = data['labels']
    
    # Convert data types for efficiency
    for col in X.select_dtypes(include=['float64']).columns:
        X[col] = X[col].astype('float32')
    for col in X.select_dtypes(include=['int64']).columns:
        X[col] = X[col].astype('int32')
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=42,
        stratify=y
    )
    
    # Train RandomForest - KEY CHANGE: Using DataFrame directly
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        min_samples_leaf=10,
        random_state=42,
        class_weight='balanced'
    )
    rf.fit(X_train, y_train)  # No .values here
    
    # Extract rules
    rules_df = improved_rule_extraction(
        rf, 
        X_train, 
        y_train,
        feature_names=FEATURE_COLUMNS,
        min_samples_leaf=20,
        accuracy_threshold=0.9
    )
    
    print(f"Valid rules extracted: {len(rules_df)}")
    if len(rules_df) > 0:
        print(rules_df.head())
        rules_df.to_csv("extracted_rules.csv", index=False)
        
        # Save model and feature list
        dump({
            'model': rf,
            'features': FEATURE_COLUMNS
        }, 'network_intrusion_rf_model.joblib')
    else:
        print("No valid rules met the criteria")