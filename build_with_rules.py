import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam


class NeuralEnhancedDetector:
    def __init__(self, config):
        self.config = config
        self.label_encoder = LabelEncoder()
        
    def build_nn(self, input_shape, num_classes):
        model = Sequential([
            Dense(128, activation='relu', input_shape=(input_shape,)),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dense(num_classes, activation='softmax')
        ])
        model.compile(
            optimizer=Adam(0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        return model

    def train_and_evaluate(self):
        # Load data
        data = pd.read_csv(self.config['DATA_PATH'])
        X = data[self.config['FEATURE_COLUMNS']]
        y = self.label_encoder.fit_transform(data[self.config['TARGET_COLUMN']])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        # Train neural network
        self.nn_model = self.build_nn(X_train.shape[1], len(np.unique(y)))
        self.nn_model.fit(
            X_train, y_train,
            epochs=20,
            batch_size=256,
            validation_split=0.2
        )
        
        # Load rules
        rules_data = load(self.config['RULES_PATH'])
        self.high_conf_rules = pd.DataFrame(rules_data)
        
        # Evaluate
        nn_preds = self.nn_model.predict(X_test).argmax(axis=1)
        enhanced_preds = self.apply_rules(X_test, nn_preds)
        
        print("NN Base Model:")
        print(classification_report(y_test, nn_preds, target_names=self.label_encoder.classes_))
        
        print("\nRule-Enhanced Model:")
        print(classification_report(y_test, enhanced_preds, target_names=self.label_encoder.classes_))

    def apply_rules(self, X, preds):
        probs = self.nn_model.predict(X)
        uncertain = np.max(probs, axis=1) < 0.7  # Low confidence threshold
        
        for _, rule in self.high_conf_rules.iterrows():
            rule_mask = self.eval_rule(rule['rule'], X)
            preds[uncertain & rule_mask] = rule['class']
        return preds