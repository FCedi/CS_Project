import pandas as pd
import re
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error

# Load dataset
df = pd.read_csv("genève.csv", encoding="latin1", sep=";")

# Copy to avoid modifying original
data = df.copy()

# --- Feature Engineering ---

# Extract ZIP code
data['zip_code'] = data['textLoadingClassname 3'].str.extract(r'(\d{4})')

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

# Drop rows with missing values in any of the features
data.dropna(subset=['zip_code', 'price', 'rooms', 'size', 'type'], inplace=True)

# Convert ZIP to numeric
data['zip_code'] = data['zip_code'].astype(float)

# --- Model Training ---

# Features and target
X = data[['zip_code', 'rooms', 'size', 'type']]
y = data['price']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Preprocessing pipeline for categorical variable
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['type'])
    ],
    remainder='passthrough'  # keep zip_code, rooms, size as-is
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
print(f"✅ Model trained. RMSE: CHF {rmse:,.2f}")

# Save model
joblib.dump(model_pipeline, "price_estimator.pkl")
print("📦 Model saved as 'price_estimator.pkl'")
