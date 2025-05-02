import numpy as np
from scikit.learn import RandomForestRegressor
import joblib

# Dummy data for training (replace later with real data)
X = np.array([
    [47.3769, 8.5417, 100, 1],
    [46.9481, 7.4474, 80, 0],
    [46.2044, 6.1432, 120, 1],
    [47.5596, 7.5886, 90, 0],
])
y = np.array([900000, 600000, 1200000, 700000])

# Train model
model = RandomForestRegressor(n_estimators=10, random_state=42)
model.fit(X, y)

# Save in current Python version
joblib.dump(model, "price_estimator.pkl")

print("✅ Model trained and saved as price_estimator.pkl")