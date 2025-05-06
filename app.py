import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import joblib
import pandas as pd
import numpy as np

st.set_page_config(page_title="Swiss Real Estate Price Estimator", layout="wide")

# ---- Load model ----
@st.cache_resource
def load_model():
    return joblib.load("price_estimator.pkl")

model = load_model()

# ---- Geocoding helper ----
@st.cache_data
def get_location(address, zip_code, city, country='CH'):
    query = f"{address}, {zip_code} {city}, {country}"
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
    response = requests.get(url, headers={'User-Agent': 'real-estate-app'})
    if response.status_code != 200:
        return None, None
    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    return None, None

# ---- Session state ----
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# ---- WELCOME PAGE ----
if st.session_state.page == "welcome":
    st.title("🏡 Swiss Real Estate Price Estimator")

    st.write("""
    This program provides you with a comparable price for your rental unit if you want to rent out your apartment or house in Geneva, Zürich, Lausanne, or St. Gallen.
    """)

    if st.button("Let's Start"):
        st.session_state.page = "input"
        st.experimental_rerun()

# ---- INPUT PAGE ----
if st.session_state.page == "input":

    st.title("Enter Property Details")

    with st.form("property_form"):

        st.header("📍 Address")
        street = st.text_input("Street and House Number")
        zip_code = st.text_input("ZIP Code", max_chars=10)
        city = st.text_input("City")

        st.header("🏠 Property Details")
        size = st.number_input("Property Size (m²)", min_value=10, max_value=1000, value=100)
        rooms = st.number_input("Number of Rooms", min_value=1.0, max_value=20.0, step=0.5, value=3.0)

        st.header("✨ Features")

        outdoor_space = st.selectbox("Outdoor Space", ["No", "Balcony", "Terrace", "Roof Terrace", "Garden"])
        is_renovated = st.radio("Is the property new or recently renovated (last 5 years)?", ["Yes", "No"])
        parking = st.selectbox("Does the property include a parking space?", ["No", "Parking Outdoor", "Garage"])

        submitted = st.form_submit_button("Estimate Price")

    if submitted:
        # Save data to session and go to result page
        st.session_state.address = street
        st.session_state.zip_code = zip_code
        st.session_state.city = city
        st.session_state.size = size
        st.session_state.rooms = rooms
        st.session_state.outdoor_space = outdoor_space
        st.session_state.is_renovated = is_renovated
        st.session_state.parking = parking
        st.session_state.page = "result"
        st.experimental_rerun()

# ---- RESULT PAGE ----
if st.session_state.page == "result":

    st.title("🏷️ Estimated Price")

    # Show entered data
    st.subheader("Property Details")
    st.write(f"**Address:** {st.session_state.address}, {st.session_state.zip_code} {st.session_state.city}")
    st.write(f"**Size:** {st.session_state.size} m²")
    st.write(f"**Rooms:** {st.session_state.rooms}")
    st.write(f"**Outdoor Space:** {st.session_state.outdoor_space}")
    st.write(f"**Recently Renovated:** {st.session_state.is_renovated}")
    st.write(f"**Parking:** {st.session_state.parking}")

    # Get location
    lat, lon = get_location(st.session_state.address, st.session_state.zip_code, st.session_state.city)

    if lat and lon:
        st.subheader("📍 Location on Map")
        m = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker(
            [lat, lon],
            popup="Property Location",
            tooltip="Property Location",
            icon=folium.Icon(color="red", icon="home", prefix='fa')
            ).add_to(m)
        st_folium(m, width=700)

    # Prepare features
    outdoor_flag = 0 if st.session_state.outdoor_space == "No" else 1
    renovated_flag = 1 if st.session_state.is_renovated == "Yes" else 0
    parking_flag = 0
    if st.session_state.parking == "Parking Outdoor":
        parking_flag = 1
    elif st.session_state.parking == "Garage":
        parking_flag = 2

    # Create input DataFrame for prediction
    features = pd.DataFrame([{
        "ZIP": float(st.session_state.zip_code),
        "number_of_rooms": st.session_state.rooms,
        "square_meters": st.session_state.size,
        "place_type": "Apartment",
        "Is_Renovated_or_New": renovated_flag,
        "Has_Parking": parking_flag,
        "Has_Outdoor_Space": outdoor_flag
    }])

    estimated_price = model.predict(features)[0]
    lower_bound = int(estimated_price * 0.9)
    upper_bound = int(estimated_price * 1.1)

    st.subheader("💰 Estimated Price Range")
    st.write(f"CHF {lower_bound:,} - CHF {upper_bound:,}")
    st.markdown(f"### ➡️ Estimated Price: **CHF {int(estimated_price):,}**")

    # Option for new entry
    if st.button("Estimate Another Property"):
        st.session_state.page = "input"
        st.experimental_rerun()