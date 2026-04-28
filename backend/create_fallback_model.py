import numpy as np
import os

print("Creating fallback model...")

# Create a dummy model for fallback (not used, but file needs to exist)
import joblib

# Simple placeholder
placeholder = {"version": "1.0", "type": "fallback"}
joblib.dump(placeholder, 'app/models/cloudburst_model.pkl')
print("Fallback model created at app/models/cloudburst_model.pkl")
