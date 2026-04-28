import os
import numpy as np
import joblib

class MLService:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLService, cls).__new__(cls)
        return cls._instance
    
    def load_model(self):
        if self._model is None:
            try:
                import tensorflow as tf
                model_path = 'app/models/cloudburst_model.h5'
                if os.path.exists(model_path):
                    self._model = tf.keras.models.load_model(model_path)
                    print(f"Model loaded from {model_path}")
                else:
                    print(f"Model not found at {model_path}")
                    self._model = None
            except Exception as e:
                print(f"Error loading model: {e}")
                self._model = None
        return self._model
    
    def predict(self, features):
        model = self.load_model()
        if model is not None:
            try:
                # Prepare input sequence
                sequence = self.preprocess_features(features)
                prediction = model.predict(sequence, verbose=0)
                return float(prediction[0][0])
            except Exception as e:
                print(f"Prediction error: {e}")
                return self._fallback_predict(features)
        else:
            return self._fallback_predict(features)
    
    def preprocess_features(self, features):
        # Create a 24-hour sequence from current features
        sequence = []
        for t in range(24):
            row = [
                features.get('temperature', 25),
                features.get('humidity', 65),
                features.get('pressure', 1013),
                features.get('wind_speed', 2.5),
                features.get('cloud_cover', 40),
                0,  # rainfall_6h
                -1, # pressure_trend
                1,  # humidity_trend
                800, # cape_value
                80   # vine_value
            ]
            sequence.append(row)
        return np.array(sequence).reshape(1, 24, 10)
    
    def _fallback_predict(self, features):
        # Rule-based fallback
        humidity_score = features.get('humidity', 50) / 100
        pressure_score = max(0, (1013 - features.get('pressure', 1013)) / 30)
        wind_score = max(0, (5 - features.get('wind_speed', 2.5)) / 10)
        cloud_score = features.get('cloud_cover', 40) / 100
        
        probability = (humidity_score * 0.4 + pressure_score * 0.3 + 
                       wind_score * 0.2 + cloud_score * 0.1)
        return min(probability, 1.0)

# Singleton instance
ml_service = MLService()
