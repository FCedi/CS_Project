import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import joblib
import numpy as np

st.set_page_config(page_title="Swiss Real Estate Price Estimator", layout="wide")
st.title("🏡 Swiss Real Estate Price Estimator")

# ---- Get User Input ----
with st.form("property_form"):
    st.subheader("Enter Property Details")

    zip_code = st.text_input("ZIP Code", max_chars=10)
    size = st.number_input("Property Size (m²)", min_value=10, max_value=1000, value=100)
    garden = st.checkbox("Has Garden?")
    
    submitted = st.form_submit_button("Estimate Price")

# ---- Helper function to get lat/lon from zip ----
@st.cache_data
def get_location_from_zip(zip_code, country='CH'):
    url = f"https://nominatim.openstreetmap.org/search?postalcode={zip_code}&country={country}&format=json"
    response = requests.get(url, headers={'User-Agent': 'real-estate-app'})
    
    if response.status_code != 200:
        return None, None
    
    data = response.json()
    
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    else:
        return None, None

# ---- Load model ----

import os

@st.cache_resource
def load_model():
    if not os.path.exists("price_estimator.pkl"):
        st.error("Model file not found. Please run train_model.py to generate the model.")
        st.stop()
    return joblib.load("price_estimator.pkl")

model = load_model()

# ---- Process form submission ----
if submitted:

    if zip_code.strip() == "":
        st.error("Please enter a valid ZIP code.")
    else:
        lat, lon = get_location_from_zip(zip_code)

        if lat is None or lon is None:
            st.error("Could not find location for the entered ZIP code.")
        else:
            # Show map
            st.subheader("📍 Property Location on Map")
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], tooltip="Your Property").add_to(m)
            st_folium(m, width=700)

            # Predict price
            st.subheader("📊 Estimated Price")

            features = np.array([[lat, lon, size, int(garden)]])
            estimated_price = model.predict(features)[0]
            
            # Calculate price range (+- 10%)
            lower_bound = int(estimated_price * 0.9)
            upper_bound = int(estimated_price * 1.1)

            st.success(f"Estimated Price Range: CHF {lower_bound:,} - CHF {upper_bound:,}")

