import numpy as np
import pandas as pd
import xarray as xr
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout, Conv1D, Bidirectional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
import os
import json

print('='*60)
print('TRAINING GRU MODEL WITH REAL IMD DATA (2023-2025)')
print('='*60)

# Load IMD data for all 3 years
districts = {
    'uttarkashi': {'lat': 30.73, 'lon': 78.45},
    'chamoli': {'lat': 30.42, 'lon': 79.33},
    'rudraprayag': {'lat': 30.28, 'lon': 78.98},
    'bageshwar': {'lat': 29.85, 'lon': 79.77},
    'pithoragarh': {'lat': 29.58, 'lon': 80.22}
}

years = [2023, 2024, 2025]
all_rainfall = []

print('\nLoading IMD rainfall data...')
for year in years:
    file_path = f'data/imd/{year}/RF25_ind{year}_rfp25.nc'
    if os.path.exists(file_path):
        ds = xr.open_dataset(file_path, engine='netcdf4')
        for district, coords in districts.items():
            point = ds.sel(
                LATITUDE=coords['lat'],
                LONGITUDE=coords['lon'],
                method='nearest'
            )
            rainfall = point.RAINFALL.values
            for day, rain in enumerate(rainfall):
                all_rainfall.append({
                    'year': year,
                    'district': district,
                    'day': day + 1,
                    'rainfall_mm': float(rain)
                })
        ds.close()
        print(f'  Loaded {year} data for {len(districts)} districts')

# Convert to DataFrame
df = pd.DataFrame(all_rainfall)
print(f'\nTotal records: {len(df)}')
print(f'Date range: Day 1 to Day 365/366')
print(f'Districts: {df["district"].unique()}')

# Create features for sequence prediction
window_size = 5
X, y = [], []

for district in districts.keys():
    district_df = df[df['district'] == district].sort_values(['year', 'day'])
    rainfall_series = district_df['rainfall_mm'].values
    
    for i in range(window_size, len(rainfall_series) - 1):
        X.append(rainfall_series[i-window_size:i])
        y.append(1 if rainfall_series[i+1] > 100 else 0)  # Cloudburst if >100mm in 24h

X = np.array(X).reshape(-1, window_size, 1)
y = np.array(y)

print(f'\nSequences created: {len(X)}')
print(f'Cloudburst events: {y.sum()} ({y.sum()/len(y)*100:.2f}%)')

# Balance the dataset (cloudburst events are rare)
cloudburst_indices = np.where(y == 1)[0]
non_cloudburst_indices = np.where(y == 0)[0]

if len(cloudburst_indices) > 0:
    # Sample equal number of non-cloudburst events
    sampled_non_cb = np.random.choice(non_cloudburst_indices, len(cloudburst_indices) * 2, replace=False)
    balanced_indices = np.concatenate([cloudburst_indices, sampled_non_cb])
    np.random.shuffle(balanced_indices)
    
    X_balanced = X[balanced_indices]
    y_balanced = y[balanced_indices]
    print(f'Balanced dataset: {len(X_balanced)} sequences')
    print(f'Cloudburst events in balanced set: {y_balanced.sum()} ({y_balanced.sum()/len(y_balanced)*100:.1f}%)')
else:
    X_balanced, y_balanced = X, y
    print('No cloudburst events found in dataset')

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42, stratify=y_train)

print(f'\nTraining samples: {len(X_train)}')
print(f'Validation samples: {len(X_val)}')
print(f'Test samples: {len(X_test)}')

# Scale features
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train.reshape(-1, window_size)).reshape(X_train.shape)
X_val_scaled = scaler.transform(X_val.reshape(-1, window_size)).reshape(X_val.shape)
X_test_scaled = scaler.transform(X_test.reshape(-1, window_size)).reshape(X_test.shape)

# Build improved GRU model
model = Sequential([
    Conv1D(32, 2, activation='relu', input_shape=(window_size, 1)),
    Dropout(0.2),
    Bidirectional(GRU(64, return_sequences=True)),
    Dropout(0.2),
    Bidirectional(GRU(32)),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

# Train
print('\nTraining model...')
history = model.fit(
    X_train_scaled, y_train,
    validation_data=(X_val_scaled, y_val),
    epochs=50,
    batch_size=32,
    verbose=1
)

# Evaluate
y_pred_prob = model.predict(X_test_scaled, verbose=0)
y_pred = (y_pred_prob > 0.5).astype(int)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
auc = roc_auc_score(y_test, y_pred_prob)

print('\n' + '='*60)
print('MODEL PERFORMANCE ON REAL IMD DATA (2023-2025)')
print('='*60)
print(f'Accuracy:  {accuracy*100:.2f}%')
print(f'Precision: {precision:.4f}')
print(f'Recall:    {recall:.4f}')
print(f'F1-Score:  {f1:.4f}')
print(f'AUC-ROC:   {auc:.4f}')

print('\n' + '='*60)
print('CLASSIFICATION REPORT')
print('='*60)
print(classification_report(y_test, y_pred, target_names=['No Cloudburst', 'Cloudburst']))

print('\n' + '='*60)
print('CONFUSION MATRIX')
print('='*60)
cm = confusion_matrix(y_test, y_pred)
print(f'True Negatives:  {cm[0][0]}  |  False Positives: {cm[0][1]}')
print(f'False Negatives: {cm[1][0]}  |  True Positives:  {cm[1][1]}')

# Save model
os.makedirs('app/models', exist_ok=True)
model.save('app/models/cloudburst_model_imd_trained.h5')
print('\nModel saved to: app/models/cloudburst_model_imd_trained.h5')

# Save scaler
import joblib
joblib.dump(scaler, 'app/models/scaler.pkl')

# Save metrics
metrics = {
    'accuracy': float(accuracy),
    'precision': float(precision),
    'recall': float(recall),
    'f1_score': float(f1),
    'auc_roc': float(auc),
    'training_samples': int(len(X_train)),
    'test_samples': int(len(X_test)),
    'cloudburst_events': int(y.sum()),
    'data_years': [2023, 2024, 2025],
    'districts': list(districts.keys())
}

with open('model_metrics_imd.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print('\nMetrics saved to: model_metrics_imd.json')
print('='*60)
print('TRAINING COMPLETE')
print('Model trained on real IMD rainfall data from 2023-2025')
print('='*60)
