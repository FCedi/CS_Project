import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error

# ---- CONFIG ----
city_files = ["geneve.csv", "lausanne.csv", "st.gallen.csv", "zurich.csv"]

# ---- Load and merge datasets ----
dfs = []
for file in city_files:
    df = pd.read_csv(file, encoding="utf-8", sep=";")  # Adjust encoding if needed
    df["source_file"] = file
    dfs.append(df)

data = pd.concat(dfs, ignore_index=True)

# ---- Preprocessing ----

# Split ZIP and City from zip_city
data[['ZIP', 'City']] = data['zip_city'].str.extract(r'(\d{4})\s*(.*)')

# Convert ZIP and numerical fields to correct types
data['ZIP'] = pd.to_numeric(data['ZIP'], errors='coerce')
data['number_of_rooms'] = pd.to_numeric(data['number_of_rooms'], errors='coerce')
data['square_meters'] = pd.to_numeric(data['square_meters'], errors='coerce')
data['rent'] = pd.to_numeric(data['rent'], errors='coerce')

# Drop rows with missing essential data
required_columns = ['ZIP', 'number_of_rooms', 'square_meters', 'place_type', 'rent']
data = data.dropna(subset=required_columns)

# ---- Feature Extraction from char.1 - char.3 ----

def detect_feature(row, keywords):
    values = [str(row['char.1']).lower(), str(row['char.2']).lower(), str(row['char.3']).lower()]
    return int(any(any(k in v for k in keywords) for v in values))

# Outdoor space detection
outdoor_keywords = ["terrace", "balcony", "garden", "patio", "loggia", "roof terrace", "outdoor"]
data['Has_Outdoor_Space'] = data.apply(lambda row: detect_feature(row, outdoor_keywords), axis=1)

# Renovated/New/Modern detection
modern_keywords = ["renovated", "new", "modern", "modern kitchen", "luxury"]
data['Is_Modern_or_New'] = data.apply(lambda row: detect_feature(row, modern_keywords), axis=1)

# Parking detection
parking_keywords = ["parking", "garage"]
data['Has_Parking'] = data.apply(lambda row: detect_feature(row, parking_keywords), axis=1)

# ---- Model Training ----

# Define features and target
X = data[['ZIP', 'number_of_rooms', 'square_meters', 'place_type', 'Is_Modern_or_New', 'Has_Parking', 'Has_Outdoor_Space']]
y = data['rent']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Preprocessing pipeline for categorical place_type
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['place_type'])
    ],
    remainder='passthrough'
)

# Full pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])

# Fit model
model_pipeline.fit(X_train, y_train)

# Evaluate
y_pred = model_pipeline.predict(X_test)
rmse = mean_squared_error(y_test, y_pred, squared=False)
print(f"✅ Unified Model trained. RMSE: CHF {rmse:,.2f}")

# Save model
joblib.dump(model_pipeline, "price_estimator.pkl")
print("📦 Model saved as 'price_estimator.pkl'")
