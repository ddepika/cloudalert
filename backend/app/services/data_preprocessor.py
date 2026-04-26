import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, Dict

class CloudburstDataPreprocessor:
    def __init__(self, sequence_length: int = 24, prediction_horizon: int = 6):
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        
        self.feature_columns = [
            'temperature', 'humidity', 'pressure', 'wind_speed',
            'cloud_cover', 'rainfall_6h', 'pressure_trend',
            'humidity_trend', 'cape_value', 'vine_value'
        ]
        
        self.scaler = MinMaxScaler()
    
    def create_sequences(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        X, y = [], []
        
        for i in range(len(data) - self.sequence_length - self.prediction_horizon):
            X.append(data.iloc[i:i + self.sequence_length][self.feature_columns].values)
            future_rainfall = data.iloc[i + self.sequence_length:i + self.sequence_length + self.prediction_horizon]['rainfall'].sum()
            y.append(1 if future_rainfall > 100 else 0)
        
        return np.array(X), np.array(y)
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        df['rainfall_6h'] = df['rainfall'].rolling(window=6, min_periods=1).sum()
        df['pressure_trend'] = df['pressure'].diff(periods=6)
        df['humidity_trend'] = df['humidity'].diff(periods=3) / 3
        
        for lag in [1, 3, 6]:
            df[f'temp_lag_{lag}h'] = df['temperature'].shift(lag)
            df[f'humidity_lag_{lag}h'] = df['humidity'].shift(lag)
            df[f'pressure_lag_{lag}h'] = df['pressure'].shift(lag)
        
        df['cloudburst_risk_score'] = (
            (df['humidity'] >= 90).astype(int) * 0.4 +
            (df['pressure_trend'] <= -3).astype(int) * 0.3 +
            (df['wind_speed'] <= 3).astype(int) * 0.2 +
            (df['cloud_cover'] >= 80).astype(int) * 0.1
        )
        
        df = df.dropna()
        return df
