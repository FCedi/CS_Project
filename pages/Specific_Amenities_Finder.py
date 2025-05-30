import streamlit as st
import requests #will enable http request for the map api
#since we use a overpass turbo api, we can use https://geopy.readthedocs.io/en/stable/
from geopy.geocoders import Nominatim #Nominatim since we are using openstreetmap api
from geopy.distance import geodesic #we need geodesic to calculate the distance on the map we will deploy using the basic radius method
import folium #enable the creation of a map in separate html file
import streamlit.components.v1 as components #to be able to create a custom compenent, here our display map https://docs.streamlit.io/develop/concepts/custom-components/intro

#set page title using https://docs.streamlit.io/ examples
st.set_page_config(page_title='Specific Amenities Finder', layout='centered')
st.title('Specific Amenities :red[Finder]')

#storing follow up infos in the map
if "map_html" not in st.session_state:
    st.session_state.map_html = None

#adress input section using https://docs.streamlit.io/ examples
st.header('Enter Your Address')
col1, col2 = st.columns([2, 1])
street = col1.text_input('Street')
house_number = col2.text_input('House Number')
zip_code = st.text_input('ZIP Code')
city = st.text_input('City')

#Input section : Potential precise location customer want to measure distance to, again https://docs.streamlit.io/
st.header('Add a Specific Location to Assess Distance')
st.write('Enter the address of a specific location, like your new place of work or your university, to see the distance from your apartment.')
compare_street = st.text_input('Specific Street')
compare_house_number = st.text_input('Specific House Number')
compare_zip_code = st.text_input('Specific ZIP Code')
compare_city = st.text_input('Specific City')

if st.button('Compare Distance'):
    geolocator = Nominatim(user_agent='streamlit_app') #creating geocoder from geopy https://geopy.readthedocs.io/en/stable/index.html?highlight=user_agent
    full_address = f"{street} {house_number}, {zip_code} {city}" #Combines the address components the user entered into one full string
    location = geolocator.geocode(full_address)

    if not location:
        st.error('Your address could not be found.') #if adress not found, no map and error message
        st.session_state.map_html = None
    else:
        lat, lon = location.latitude, location.longitude
        st.success(f'Found your address: {location.address} ({lat:.5f}, {lon:.5f})') #if found assign geoloc values and windows pop
#creating and custmozing app according to input with a marker
        folium_map = folium.Map(location=[lat, lon], zoom_start=14)
        folium.Marker(
            [lat, lon],
            tooltip='Your Location',
            icon=folium.Icon(color='blue', icon="home")
        ).add_to(folium_map) #add custom marker to the map

        if compare_street and compare_zip_code and compare_city:
            compare_address = f'{compare_street} {compare_house_number}, {compare_zip_code} {compare_city}'
            compare_location = geolocator.geocode(compare_address)

            if compare_location:
                compare_lat = compare_location.latitude
                compare_lon = compare_location.longitude
                dist_to_compare = geodesic((lat, lon), (compare_lat, compare_lon)).meters

                folium.Marker(
                    [compare_lat, compare_lon],
                    tooltip=f'Specific Location — {dist_to_compare:.0f} m',
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(folium_map) #marks spesific location

                folium.PolyLine(
                    locations=[(lat, lon), (compare_lat, compare_lon)],
                    color='red', weight=2.5, opacity=0.8,
                    tooltip=f'{dist_to_compare:.0f} m'
                ).add_to(folium_map)

                st.info(f'Distance to specific location: **{dist_to_compare:.0f} meters**')
            else:
                st.warning('Specific location could not be found.')

        st.session_state.map_html = folium_map._repr_html_()

# Display map
if st.session_state.map_html:
    st.subheader('Distance to Spesific Amenity')
    components.html(st.session_state.map_html, height=500)
