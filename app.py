import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import joblib
import numpy as np

# ---- App Config ----
st.set_page_config(page_title="Swiss Real Estate Price Estimator", layout="wide")
st.title("🏡 Swiss Real Estate Price Estimator")

st.markdown("""
This program provides you with a comparable price for your rental unit if you want to rent out an apartment in **Geneva**, **Zürich**, **Lausanne**, or **St. Gallen**.

Simply enter your property details below and get an instant estimated price range based on our data model.
""")

# ---- Load Model ----
@st.cache_resource
def load_model():
    return joblib.load("price_estimator.pkl")

model = load_model()

# ---- Helper function to get lat/lon from address ----
@st.cache_data
def get_location_from_address(address, country='CH'):
    url = f"https://nominatim.openstreetmap.org/search?q={address}&country={country}&format=json"
    response = requests.get(url, headers={'User-Agent': 'real-estate-app'})
    
    if response.status_code != 200:
        return None, None
    
    data = response.json()
    
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    else:
        return None, None

# ---- Property Input Form ----
with st.form("property_form"):
    st.subheader("Enter Property Details")

    address = st.text_input("Property Address (Street, ZIP, City)")
    zip_code = st.text_input("ZIP Code", max_chars=10)
    size = st.number_input("Property Size (m²)", min_value=10, max_value=1000, value=100)
    rooms = st.number_input("Number of Rooms", min_value=1, max_value=20, value=3)

    # Outdoor space
    has_outdoor_space = st.checkbox("Has Outdoor Space?")
    outdoor_space_type = None
    if has_outdoor_space:
        outdoor_space_type = st.selectbox("Select Outdoor Space Type", ["Balcony", "Terrace", "Rooftop Terrace", "Garden"])

    # Renovation / Modern
    renovated_or_new = st.checkbox("Is the property renovated or new?")
    modern = st.checkbox("Is the property modern?")

    # Parking / Garage
    parking_or_garage = st.checkbox("Includes Parking or Garage?")

    # Property type
    property_type = st.selectbox("Property Type", ["Apartment", "House", "Duplex"])

    submitted = st.form_submit_button("Estimate Price")

# ---- Process Form Submission ----
if submitted:
    if zip_code.strip() == "" or address.strip() == "":
        st.error("Please enter both a valid address and ZIP code.")
    else:
        lat, lon = get_location_from_address(address)

        if lat is None or lon is None:
            st.error("Could not find location for the entered address.")
        else:
            # Save form results to session state
            st.session_state['result'] = {
                'address': address,
                'zip_code': zip_code,
                'lat': lat,
                'lon': lon,
                'size': size,
                'rooms': rooms,
                'outdoor_space': has_outdoor_space,
                'outdoor_type': outdoor_space_type,
                'renovated_or_new': renovated_or_new,
                'modern': modern,
                'parking_or_garage': parking_or_garage,
                'property_type': property_type
            }

# ---- Display Results if Available ----
if 'result' in st.session_state:
    result = st.session_state['result']

    st.subheader("📍 Property Location on Map")
    m = folium.Map(location=[result['lat'], result['lon']], zoom_start=16)
    folium.Marker([result['lat'], result['lon']], tooltip=result['address']).add_to(m)
    st_folium(m, width=700)

    st.subheader("📊 Estimated Price")

    # Prepare features
    features = np.array([[
        float(result['zip_code']),
        result['rooms'],
        result['size'],
        result['property_type'],
        int(result['renovated_or_new']),
        int(result['modern']),
        int(result['parking_or_garage']),
        0  # renovation_needed, assumed 0 for this UI (or can make another checkbox later)
    ]])

    # Process property type manually (as model expects OneHotEncoder)
    # → Let model pipeline handle encoding
    estimated_price = model.predict(features)[0]

    # Calculate price range (+- 10%)
    lower_bound = int(estimated_price * 0.9)
    upper_bound = int(estimated_price * 1.1)

    st.success(f"Estimated Price Range: CHF {lower_bound:,} - CHF {upper_bound:,}")

    # Summary
    st.markdown("**Property Summary**")
    st.write(result)
