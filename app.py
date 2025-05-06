import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import joblib
import numpy as np

st.set_page_config(page_title="Swiss Real Estate Price Estimator", layout="wide")
st.title("🏡 Swiss Real Estate Price Estimator")

st.write("""
This program provides you with a comparable price for your rental unit if you want to rent out your apartment or house in Geneva, Zürich, Lausanne, or St. Gallen.
""")

# ---- Helper function to get lat/lon from address ----
@st.cache_data
def get_location_from_address(address, country='CH'):
    url = f"https://nominatim.openstreetmap.org/search?street={address}&country={country}&format=json"
    response = requests.get(url, headers={'User-Agent': 'real-estate-app'})

    if response.status_code != 200:
        return None, None

    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    else:
        return None, None

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
@st.cache_resource
def load_model():
    return joblib.load("price_estimator.pkl")

model = load_model()

# ---- Get User Input ----
with st.form("property_form"):
    st.subheader("Enter Property Details")

    street = st.text_input("Street and House Number")
    zip_code = st.text_input("ZIP Code", max_chars=10)
    city = st.text_input("City")
    
    size = st.number_input("Property Size (m²)", min_value=10, max_value=1000, value=100)
    rooms = st.number_input("Number of Rooms", min_value=1.0, max_value=20.0, step=0.5, value=3.0)

    # Outdoor space
    has_outdoor_space = st.radio("Does the property have outdoor space?", ["No", "Yes"])
    outdoor_type = None
    if has_outdoor_space == "Yes":
        outdoor_type = st.selectbox("What type of outdoor space?", ["Balcony", "Terrace", "Roof Terrace", "Garden"])

    # Renovated / Modern / Parking
    is_renovated = st.radio("Is the property new or recently renovated (last 5 years)?", ["Yes", "No"])
    is_modern = st.radio("Does the property have modern features (e.g. insulated windows or central heating, new kitchen/bathroom)?", ["Yes", "No"])
    parking_type = st.selectbox("Does the property include a parking space?", ["No", "Parking Outdoor", "Garage"])

    submitted = st.form_submit_button("Estimate Price")

# ---- Process form submission ----
if submitted:

    if zip_code.strip() == "":
        st.error("Please enter a valid ZIP code.")
    else:
        full_address = f"{street}, {zip_code} {city}"

        lat, lon = get_location_from_address(full_address)

        if lat is None or lon is None:
            lat, lon = get_location_from_zip(zip_code)

        if lat is None or lon is None:
            st.error("Could not find location for the entered address or ZIP code.")
        else:
            # Show map
            st.subheader("📍 Property Location on Map")
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], tooltip="Your Property").add_to(m)
            st_folium(m, width=700)

            # Prepare features
            outdoor_space_flag = 1 if has_outdoor_space == "Yes" else 0
            renovated_flag = 1 if is_renovated == "Yes" else 0
            modern_flag = 1 if is_modern == "Yes" else 0
            parking_flag = 0
            if parking_type == "Parking Outdoor":
                parking_flag = 1
            elif parking_type == "Garage":
                parking_flag = 2

            # Predict price
            st.subheader("📊 Estimated Price")

            features = np.array([[float(zip_code), rooms, size, "Apartment", renovated_flag, modern_flag, parking_flag, outdoor_space_flag]])
            estimated_price = model.predict(features)[0]

            lower_bound = int(estimated_price * 0.9)
            upper_bound = int(estimated_price * 1.1)

            st.success(f"Estimated Price Range: CHF {lower_bound:,} - CHF {upper_bound:,}")

