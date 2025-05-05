import pandas as pd
import re
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
    df = pd.read_csv(file, encoding="latin1", sep=";")
    df["source_file"] = file  # track source city
    dfs.append(df)

data = pd.concat(dfs, ignore_index=True)

# ---- Feature Engineering ----

# Extract ZIP code
data['zip_code'] = data['textLoadingClassname 3'].str.extract(r'(\d{4})')

# Convert ZIP code to numeric, coercing errors (invalid ZIP → NaN)
data['zip_code'] = pd.to_numeric(data['zip_code'], errors='coerce')

# Drop rows with missing ZIP codes
data = data.dropna(subset=['zip_code'])

# Convert ZIP code to float
data['zip_code'] = data['zip_code'].astype(float)

# Clean and convert price
data['price'] = (
    data['textLoadingClassname 4']
    .str.replace(r'[^\d]', '', regex=True)
    .replace('', pd.NA)
    .astype(float)
)

# Extract number of rooms
data['rooms'] = data['textLoadingClassname 2'].str.extract(r'(\d+)\s*rooms').astype(float)

# Extract property size in m²
data['size'] = data['textLoadingClassname 2'].str.extract(r'(\d+)\s*m²').astype(float)

# Extract property type
data['type'] = (
    data['textLoadingClassname 2']
    .str.extract(r'(Apartment|House|Duplex)', flags=re.IGNORECASE, expand=False)
    .str.capitalize()
    .fillna('Apartment')
)

# Detect outdoor space (optional)
outdoor_keywords = ['balcony', 'terrace', 'garden', 'loggia', 'patio', 'roof terrace', 'veranda', 'outdoor']
data['has_outdoor_space'] = data['textLoadingClassname 2'].str.contains(
    '|'.join(outdoor_keywords), flags=re.IGNORECASE, regex=True, na=False
)

# Detect price influencing factors
data['renovated_or_new'] = data['textLoadingClassname 2'].str.contains('renovated|newly renovated|new', flags=re.IGNORECASE, regex=True, na=False).astype(int)
data['modern'] = data['textLoadingClassname 2'].str.contains('modern', flags=re.IGNORECASE, regex=True, na=False).astype(int)
data['parking_or_garage'] = data['textLoadingClassname 2'].str.contains('parking|garage', flags=re.IGNORECASE, regex=True, na=False).astype(int)
data['renovation_needed'] = data['textLoadingClassname 2'].str.contains('renovation needed', flags=re.IGNORECASE, regex=True, na=False).astype(int)

# Drop rows with missing values in any of the required features
data.dropna(subset=['price', 'rooms', 'size', 'type'], inplace=True)

# ---- Model Training ----

# Features and target
X = data[['zip_code', 'rooms', 'size', 'type', 'renovated_or_new', 'modern', 'parking_or_garage', 'renovation_needed']]
y = data['price']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Preprocessing pipeline for categorical variable
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['type'])
    ],
    remainder='passthrough'  # keep zip_code, rooms, size, and binary flags as-is
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
