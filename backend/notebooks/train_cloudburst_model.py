import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, Bidirectional, Conv1D
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import os

class CloudburstPredictor:
    def __init__(self, input_shape: tuple, model_type: str = 'gru', units: int = 64, dropout_rate: float = 0.2):
        self.input_shape = input_shape
        self.model_type = model_type
        self.units = units
        self.dropout_rate = dropout_rate
        self.model = None
        self.history = None
    
    def build_model(self):
        model = Sequential()
        
        model.add(Conv1D(filters=32, kernel_size=3, activation='relu', input_shape=self.input_shape))
        model.add(Dropout(self.dropout_rate))
        
        if self.model_type == 'lstm':
            model.add(LSTM(self.units, return_sequences=True))
            model.add(Dropout(self.dropout_rate))
            model.add(LSTM(self.units // 2))
        elif self.model_type == 'gru':
            model.add(GRU(self.units, return_sequences=True))
            model.add(Dropout(self.dropout_rate))
            model.add(GRU(self.units // 2))
        elif self.model_type == 'bilstm':
            model.add(Bidirectional(LSTM(self.units, return_sequences=True)))
            model.add(Dropout(self.dropout_rate))
            model.add(Bidirectional(LSTM(self.units // 2)))
        
        model.add(Dense(32, activation='relu'))
        model.add(Dropout(self.dropout_rate))
        model.add(Dense(1, activation='sigmoid'))
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=0.00001)
        checkpoint = ModelCheckpoint('best_cloudburst_model.h5', monitor='val_accuracy', save_best_only=True)
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop, reduce_lr, checkpoint],
            verbose=1
        )
        
        self.model = tf.keras.models.load_model('best_cloudburst_model.h5')
        return self.history
    
    def evaluate(self, X_test, y_test):
        loss, accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        y_pred_prob = self.model.predict(X_test, verbose=0)
        y_pred = (y_pred_prob > 0.5).astype(int)
        
        print(f"\\nModel Evaluation ({self.model_type.upper()}):")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"AUC-ROC: {roc_auc_score(y_test, y_pred_prob):.4f}")
        
        return {'accuracy': accuracy, 'auc_roc': roc_auc_score(y_test, y_pred_prob)}
    
    def save_model(self, filepath: str):
        self.model.save(filepath)
        print(f"Model saved to {filepath}")

def prepare_sample_data():
    np.random.seed(42)
    n_samples = 5000
    sequence_length = 24
    n_features = 10
    
    X = np.random.randn(n_samples, sequence_length, n_features)
    y = np.zeros(n_samples)
    
    for i in range(n_samples):
        avg_humidity = X[i, :, 1].mean()
        avg_pressure = X[i, :, 2].mean()
        if avg_humidity > 0.7 and avg_pressure < 0.3:
            y[i] = np.random.choice([0, 1], p=[0.3, 0.7])
        else:
            y[i] = np.random.choice([0, 1], p=[0.95, 0.05])
    
    return X, y

def main():
    print("="*60)
    print("Cloudburst Prediction Model Training")
    print("="*60)
    
    print("\\n1. Loading sample data...")
    X, y = prepare_sample_data()
    
    print("2. Splitting data...")
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
    
    print(f"   Training: {len(X_train)} samples")
    print(f"   Validation: {len(X_val)} samples")
    print(f"   Test: {len(X_test)} samples")
    
    print("\\n3. Training GRU model...")
    predictor = CloudburstPredictor(
        input_shape=(X.shape[1], X.shape[2]),
        model_type='gru',
        units=128,
        dropout_rate=0.3
    )
    predictor.build_model()
    predictor.model.summary()
    
    predictor.train(X_train, y_train, X_val, y_val, epochs=30)
    results = predictor.evaluate(X_test, y_test)
    
    # Save model
    os.makedirs('../app/models', exist_ok=True)
    predictor.save_model('../app/models/cloudburst_model.h5')
    
    print("\\nTraining complete! Model saved to app/models/cloudburst_model.h5")

if __name__ == "__main__":
    main()
