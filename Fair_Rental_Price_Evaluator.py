import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import joblib
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt # For Diagrams
import math
from geopy.geocoders import Nominatim # For Amenities
from geopy.distance import geodesic 
import streamlit.components.v1 as components
import time # helps to prevent API crashes 

#Variables that always exist and prevent crashes when reloading the page at the wrong time
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "city" not in st.session_state:
    st.session_state.city = ""
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
if "amenities" not in st.session_state:
    st.session_state.amenities = []
if "radius" not in st.session_state:
    st.session_state.radius = 300

st.set_page_config(page_title="Fair Rental Price Evaluator", layout="wide")

# Load model (price estimator)
@st.cache_resource
def load_model():
    return joblib.load("price_estimator.pkl")

model_pipeline = load_model()

@st.cache_data
# gets apartment location and map from openstreetmap
def get_location(address, zip_code, city, country='CH'):
    query = f"{address}, {zip_code} {city}, {country}"
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
    
    time.sleep(1)  # pause 1 sec to prevent crashes and too many requests
    
    response = requests.get(url, headers={'User-Agent': 'streamlit_app (cedric.frutiger@startglobal.org)'}) # user-agent to prevent api crashes
    if response.status_code != 200:
        return None, None
    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    return None, None

# gets amenities and there location from overpass
def get_amenity_elements(amenity, lat, lon, radius):
    key = f"amenity_data_{amenity.lower()}"
    if key in st.session_state:
        return st.session_state[key]

    # changes of user tags to actual osm tags
    tag_mapping = {
        "supermarket": ("shop", "supermarket"),
        "school": ("amenity", "school"),
        "hospital": ("amenity", "hospital"),
        "pharmacy": ("amenity", "pharmacy"),
        "restaurant": ("amenity", "restaurant")
    }
    # fallback for not found amenities
    tag_key, tag_value = tag_mapping.get(amenity.lower(), ("amenity", amenity.lower()))

    query = f"""
    [out:json];
    (
      node["{tag_key}"="{tag_value}"](around:{radius},{lat},{lon});
      way["{tag_key}"="{tag_value}"](around:{radius},{lat},{lon});
      relation["{tag_key}"="{tag_value}"](around:{radius},{lat},{lon});
    );
    out center;
    """

    try:
        response = requests.post("https://overpass-api.de/api/interpreter", data=query, timeout=30)
        response.raise_for_status()
        elements = response.json().get("elements", [])
        st.session_state[key] = elements
        return elements
    except Exception as e:
        st.error(f"Failed to retrieve amenities for {amenity}: {e}")
    return []

# Get average price per m2 per year from training csv files
city_files = {
    "Geneva": "geneve.csv",
    "Lausanne": "lausanne.csv",
    "Zurich": "zurich.csv",
    "St. Gallen": "st.gallen.csv"
}

zip_avg_p_sqm_y = {}
for city, filename in city_files.items():
    if os.path.exists(filename):
        df = pd.read_csv(filename, encoding="latin1", sep=";")
        df[['ZIP', 'City']] = df['zip_city'].str.extract(r'(\d{4})\s*(.*)')
        df['ZIP'] = pd.to_numeric(df['ZIP'], errors='coerce')
        df['p/squarem/y'] = df['p/squarem/y'].astype(str).str.replace(r"[^\d.]", "", regex=True) # only takes numereical value from p/squarem/y
        df['p/squarem/y'] = pd.to_numeric(df['p/squarem/y'], errors='coerce')# prevents "No market price data available for this city." output
        
        grouped = df.dropna(subset=['ZIP', 'p/squarem/y']).groupby('ZIP')['p/squarem/y'].mean()
        for zip_code, avg_price in grouped.items():
            zip_avg_p_sqm_y[int(zip_code)] = round(avg_price, 2)

# Checks for a session state (avoids reruns and errors when displaxint the results)
# If nothing is found go to welcome page
if "page" not in st.session_state:
    st.session_state.page = "welcome"


# WELCOME PAGE
if st.session_state.page == "welcome":
    st.title("Fair Rental Price Evaluator")
    
    # display on the welcome page
    st.write("""
        **Are you relocating to a new city and want to know if you’re getting a good deal?**\n
        With so many real estate platforms available, it's hard to tell if you have a good offer in front of you, where exactly you'll be located in \
        the new city, and what is nearby.\n
        To help with this, we developed an app that gives you a fair price range for your apartment based on its size and features such as outdoor \
        space, recent renovations, and parking availability. Additionally, it provides a comparison between your price per square meter and the city \
        average.\n
        If you want to see the distance to a specific location like your workplace or university, select the Specific Amenities Finder in the side menu.
    """)

    if st.button("Let's Start"):
        st.session_state.page = "input"
        st.rerun()
    
    st.caption("This program is currently in development and only trained on apartments in Geneva, Zurich, Lausanne, and St. Gallen.")


# INPUT PAGE
if st.session_state.page == "input":

    st.title("Enter Property Details")

    with st.form("property_form"):

        st.header("Address")
        street = st.text_input("Street and House Number")
        zip_code = st.text_input("ZIP Code", max_chars=4)
        city = st.text_input("City")
        st.caption("Please write the city name the english way (NO Ä, Ü, Ö).")

        st.header("Property Details")
        size = st.number_input("Property Size (m²)", min_value=10, max_value=1000, step=5, value=100)
        rooms = st.number_input("Number of Rooms", min_value=1.0, max_value=20.0, step=0.5, value=3.0)
        demanded_rent = st.number_input("Demanded Rent (CHF)", min_value=100, max_value=20000, value=1500)
        st.caption("Please enter the rent rounded in CHF.")

        st.header("Features")
        outdoor_space = st.selectbox("Outdoor Space", ["No", "Balcony", "Terrace", "Roof Terrace", "Garden"])
        is_renovated = st.radio("Is the property new or recently renovated (last 5 years)?", ["Yes", "No"])
        parking = st.selectbox("Does the property include a parking space?", ["No", "Parking Outdoor", "Garage"])

        st.header("Amenities")
        st.caption("The amenities will not influence the estimated rent. This will show what is close to your entered apartment.")
        amenity_options = ["Supermarket", "School", "Hospital", "Pharmacy", "Restaurant"]
        amenities = [a for a in amenity_options if st.checkbox(a, key=f"chk_{a}")]
        radius = st.slider("Search Radius in meters", 100, 3000, 500)

        submitted = st.form_submit_button("Compare your Rent")

    # Save data to session and go to result page
    if submitted:
        st.session_state.address = street
        st.session_state.zip_code = zip_code
        st.session_state.city = city
        st.session_state.size = size
        st.session_state.rooms = rooms
        st.session_state.demanded_rent = demanded_rent
        st.session_state.outdoor_space = outdoor_space
        st.session_state.is_renovated = is_renovated
        st.session_state.parking = parking
        st.session_state.amenities = amenities
        st.session_state.radius = radius
        st.session_state.page = "result"
        st.rerun()


# RESULT PAGE
if st.session_state.page == "result":

    st.title("Fair Estimated Rent")

    # Show entered data from input page
    st.subheader("Property Details")
    st.write(f"**Address:** {st.session_state.address}, {st.session_state.zip_code} {st.session_state.city}")
    st.write(f"**Size:** {st.session_state.size} m²")
    st.write(f"**Rooms:** {st.session_state.rooms}")
    st.write(f"**Demanded Rent:** {st.session_state.demanded_rent} CHF")
    st.write(f"**Outdoor Space:** {st.session_state.outdoor_space}")
    st.write(f"**Recently Renovated:** {st.session_state.is_renovated}")
    st.write(f"**Parking:** {st.session_state.parking}")
    
    # Edit button to return to input page
    if st.button("Edit Property Details"):
        st.session_state.page = "input"
        st.rerun()

    # Market price calculation with average price per m2 per year comparison
    user_zip = int(st.session_state.zip_code)
    market_price_m2_y = zip_avg_p_sqm_y.get(user_zip)

    # analyse inputs from input page and prep for estimation
    outdoor_flag = 0 if st.session_state.outdoor_space == "No" else 1
    renovated_flag = 1 if st.session_state.is_renovated == "Yes" else 0
    parking_flag = 0
    if st.session_state.parking == "Parking Outdoor":
            parking_flag = 1
    elif st.session_state.parking == "Garage":
            parking_flag = 2
    
    # defins features for estimation and diagrams
    features = pd.DataFrame([{
        "ZIP": float(st.session_state.zip_code) if st.session_state.zip_code else 0.0,
        "number_of_rooms": st.session_state.rooms,
        "square_meters": st.session_state.size,
        "place_type": "Apartment",
        "Is_Renovated_or_New": renovated_flag,
        "Has_Parking": parking_flag,
        "Has_Outdoor_Space": outdoor_flag
        }])

    estimated_price = model_pipeline.predict(features)[0]
    st.session_state.estimated_price = estimated_price # Saves the estimated price

    col1, col2 = st.columns(2)

    with col1: # left side display below the Map
        if market_price_m2_y is not None and not math.isnan(market_price_m2_y):

            market_estimated_price = (market_price_m2_y / 12) * st.session_state.size

            st.subheader("Price per m² per Year Comparison")

            user_m2_price_year = (estimated_price / st.session_state.size) * 12

            labels = ['Your Property', 'Market Average in your City']
            values = [user_m2_price_year, market_price_m2_y]

            fig, ax = plt.subplots(figsize=(8, 6))
            bars = ax.bar(labels, values, color=["green", "blue"])
            ax.set_ylabel("CHF per m² per year")
            ax.set_title(f"Price per m²/year Comparison (ZIP {user_zip})")

            # Add value labels on bars
            for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2, height + 5, f"{int(height)} CHF", ha='center', va='bottom')

            st.pyplot(fig)

        # Happens when city is not in the training data
        else:
            st.warning("No market price data available for this city.")

    with col2: # right side display below the distande of the Amenities
        
        st.subheader("Your Rent Compared to our Prediction")

        # Load diagnostics
        X_test, y_test, _ = joblib.load("model_diagnostics.pkl")
        y_pred = model_pipeline.predict(X_test)

        # Add user's data point
        if "demanded_rent" in st.session_state and st.session_state.demanded_rent > 0:
            actual = st.session_state.demanded_rent
            predicted = st.session_state.estimated_price

            # Plot
            import matplotlib.pyplot as plt

            plt.figure(figsize=(8, 6))
            plt.scatter(y_test, y_pred, alpha=0.6, label='Training Data Predictions')
            plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 'r--', label='Ideal Prediction Line')

            # Add user point
            plt.scatter(actual, predicted, color='red', s=100, label='Entered Apartment')
            plt.xlabel("Actual Rent (CHF)")
            plt.ylabel("Predicted Rent (CHF)")
            plt.title("Predicted vs. Actual Rent Price")
            st.pyplot(plt)

    lower_bound = int(estimated_price * 0.9)
    upper_bound = int(estimated_price * 1.1)

    st.subheader("Estimated Price Range")
    st.write(f"CHF {lower_bound:,} - CHF {upper_bound:,}")
    st.write(f"Estimated Price: **CHF {int(estimated_price):,}**")

    col1, col2 = st.columns(2)

    with col1:  # left side of the page
        st.subheader("Property Location & Nearby Amenities")

        # Get location and show location
        lat, lon = get_location(st.session_state.address, st.session_state.zip_code, st.session_state.city)

        if lat and lon:
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([
                lat, lon
            ], tooltip="Your Property", icon=folium.Icon(color="blue", icon="home", prefix='fa')).add_to(m)

            # Display amenities
            geolocator = Nominatim(user_agent='streamlit_app')
            for amenity in st.session_state.amenities:
                data = get_amenity_elements(amenity, lat, lon, st.session_state.radius)
                for el in data[:3]:
                    el_lat = el.get('lat') or el.get('center', {}).get('lat')
                    el_lon = el.get('lon') or el.get('center', {}).get('lon')
                    if el_lat and el_lon:
                        dist = geodesic((lat, lon), (el_lat, el_lon)).meters
                        name = el.get('tags', {}).get('name', f"{amenity.title()} (Unnamed)")
                        folium.Marker(
                            [el_lat, el_lon],
                            tooltip=f"{name} — {dist:.0f} m",
                            icon=folium.Icon(color='green', icon='info-sign')
                        ).add_to(m)

            st_folium(m, width=600, height=400)
        else:
            st.warning("Could not locate your address on the map.")

    with col2:  # right side of the page 
        st.subheader("Distance to selected Amenities")

        if lat and lon and st.session_state.amenities:
            total_displayed = 0  # Counter to limit overall output
            max_results = 9

            for amenity in st.session_state.amenities:
                try:
                    data = get_amenity_elements(amenity, lat, lon, st.session_state.radius)
                    distances = []

                    for el in data:
                        el_lat = el.get("lat") or el.get("center", {}).get("lat")
                        el_lon = el.get("lon") or el.get("center", {}).get("lon")
                        if el_lat and el_lon:
                            dist = geodesic((lat, lon), (el_lat, el_lon)).meters
                            name = el.get("tags", {}).get("name", "Unnamed")
                            distances.append((name, int(dist)))

                    # Sort and limit top 3 per amenity
                    distances = sorted(distances, key=lambda x: x[1])[:3]

                    for name, dist in distances:
                        if total_displayed >= max_results:
                            break
                        st.write(f"🔹 {amenity.title()}: **{name}** — {dist} m")
                        total_displayed += 1

                except Exception as e:
                    st.error(f"Error retrieving {amenity.title()}: {e}")
        
    # Option for new entry, goes back to input page
    if st.button("Estimate Another Property"):
        st.session_state.page = "input"
        st.rerun()