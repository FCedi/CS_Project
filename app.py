import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import joblib
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import math

#Variables that always exist and prevent craches
if "page" not in st.session_state:
    st.session_state.page = "welcome"

if "city" not in st.session_state:
    st.session_state.city = None

if "zip_code" not in st.session_state:
    st.session_state.zip_code = ""

if "address" not in st.session_state:
    st.session_state.address = ""

if "size" not in st.session_state:
    st.session_state.size = 0

if "rooms" not in st.session_state:
    st.session_state.rooms = 0

if "outdoor_space" not in st.session_state:
    st.session_state.outdoor_space = "No"

if "is_renovated" not in st.session_state:
    st.session_state.is_renovated = "No"

if "parking" not in st.session_state:
    st.session_state.parking = "No"

st.set_page_config(page_title="Swiss Real Estate Price Estimator", layout="wide")

# Load model (price estimator)
@st.cache_resource
def load_model():
    return joblib.load("price_estimator.pkl")

model = load_model()

# OpenStreetMap API
# gets latitude and longitude from address input
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

# Get average price per m2 per year from training csv files
city_files = {
    "Geneva": "geneve.csv",
    "Lausanne": "lausanne.csv",
    "Zurich": "zurich.csv",
    "St. Gallen": "st.gallen.csv"
}

city_avg_p_sqm_y = {}

for city, filename in city_files.items():
    if os.path.exists(filename):
        df = pd.read_csv(filename, encoding="latin1", sep=";")
        df['p/squarem/y'] = df['p/squarem/y'].astype(str).str.replace(r"[^\d.]", "", regex=True) # only takes numereical value from p/squarem/y
        df['p/squarem/y'] = pd.to_numeric(df['p/squarem/y'], errors='coerce') # prevents "No market price data available for this city." output
        avg = df['p/squarem/y'].mean()  # directly calculates the averag
        city_avg_p_sqm_y[city] = round(avg, 2)

# Checks for a session state (avoids reruns and errors when displaxint the results)
# If nothing is found go to welcome page
if "page" not in st.session_state:
    st.session_state.page = "welcome"


# WELCOME PAGE
if st.session_state.page == "welcome":
    st.title("🏡 Swiss Real Estate Price Estimator")
    
    # display on the welcome page
    st.write("""
    This program provides you with a comparable price for your rental unit if you want to rent out your apartment or house in Geneva, Zürich, Lausanne, or St. Gallen.
    """)

    if st.button("Let's Start"):
        st.session_state.page = "input"
        st.experimental_rerun()


# INPUT PAGE
if st.session_state.page == "input":

    st.title("Enter Property Details")

    with st.form("property_form"):

        st.header("📍 Address")
        street = st.text_input("Street and House Number")
        zip_code = st.text_input("ZIP Code", max_chars=4)
        city = st.text_input("City")

        st.header("🏠 Property Details")
        size = st.number_input("Property Size (m²)", min_value=10, max_value=1000, step=5, value=100)
        rooms = st.number_input("Number of Rooms", min_value=1.0, max_value=20.0, step=0.5, value=3.0)

        st.header("✨ Features")
        outdoor_space = st.selectbox("Outdoor Space", ["No", "Balcony", "Terrace", "Roof Terrace", "Garden"])
        is_renovated = st.radio("Is the property new or recently renovated (last 5 years)?", ["Yes", "No"])
        parking = st.selectbox("Does the property include a parking space?", ["No", "Parking Outdoor", "Garage"])

        submitted = st.form_submit_button("Estimate Rent")

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


# RESULT PAGE
if st.session_state.page == "result":

    st.title("🏷️ Estimated Price")

    # Show entered data from input page
    st.subheader("Property Details")
    st.write(f"**Address:** {st.session_state.address}, {st.session_state.zip_code} {st.session_state.city}")
    st.write(f"**Size:** {st.session_state.size} m²")
    st.write(f"**Rooms:** {st.session_state.rooms}")
    st.write(f"**Outdoor Space:** {st.session_state.outdoor_space}")
    st.write(f"**Recently Renovated:** {st.session_state.is_renovated}")
    st.write(f"**Parking:** {st.session_state.parking}")

    col1, col2 = st.columns(2)  # Splits the rest of the page in two columns

    with col1:  # left side of the page
        st.subheader("📍 Property Location")

        # Get location and show location
        lat, lon = get_location(st.session_state.address, st.session_state.zip_code, st.session_state.city)

        if lat and lon:
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker(
                [lat, lon],
                popup="Property Location",
                tooltip="Property Location",
                icon=folium.Icon(color="red", icon="home", prefix='fa')
            ).add_to(m)

            st_folium(m, width=600, height=400)

        else:
            st.warning("Could not find this location on the map.")

    with col2: # right side of the page 

        # analyse inputs from input page and prep for estimation
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

        st.write("💰 Estimated Price Range")
        st.write(f"CHF {lower_bound:,} - CHF {upper_bound:,}")
        st.markdown(f"### ➡️ Estimated Price: **CHF {int(estimated_price):,}**")

    # Market price calculation with average price per m2 per year comparison
    selected_city = st.session_state.city
    market_price_m2_y = city_avg_p_sqm_y.get(selected_city)

    if market_price_m2_y is not None and not math.isnan(market_price_m2_y):

        market_estimated_price = (market_price_m2_y / 12) * st.session_state.size

        st.subheader("📊 Market Average Price (based on current listings)")
        st.write(f"Market Avg Rent Estimate: CHF {int(market_estimated_price):,}")

        st.subheader("📦 Price per m² per Year Comparison")

        user_m2_price_year = (estimated_price / st.session_state.size) * 12

        labels = ['Your Property', 'Market Average in your City']
        values = [user_m2_price_year, market_price_m2_y]

        fig, ax = plt.subplots()
        bars = ax.bar(labels, values, color=["green", "blue"])
        ax.set_ylabel("CHF per m² per year")
        ax.set_title("Price per m²/year Comparison")

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height + 5, f"{int(height)} CHF", ha='center', va='bottom')

        st.pyplot(fig)

    else:
        # Happens when city is not in the training data
        st.warning("No market price data available for this city.")

    # Option for new entry, goes back to input page
    if st.button("Estimate Another Property"):
        st.session_state.page = "input"
        st.experimental_rerun()