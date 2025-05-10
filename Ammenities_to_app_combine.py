import streamlit as st
import requests #will enable http request for the map api
#since i will try to use a geostreetmap api, we can use https://geopy.readthedocs.io/en/stable/
from geopy.geocoders import Nominatim #Nominatim since we are using openstreetmap api
from geopy.distance import geodesic #we need geodesic to calculate the distance on the map we will deploy using the basic radius method
import folium #enable the creation of a map in separate html file
import streamlit.components.v1 as components #to be able to create a custom compenent, here our display map https://docs.streamlit.io/develop/concepts/custom-components/intro




#set page title using https://docs.streamlit.io/ examples
st.set_page_config(page_title='Local Amenities Finder', layout='centered')
st.title('Local Amenities :red[Finder]')

#adress input section using https://docs.streamlit.io/ examples
st.header('Enter Your Address')
col1, col2 = st.columns([2, 1])
col1.text_input('Street')
col2.text_input('House Number')
st.text_input("ZIP Code")
st.text_input("City")

#Input section : Potential precise location customer want to measure distance to, again https://docs.streamlit.io/
st.header('Add a Target Location to Assess Distance')
st.text_input('Target Street')
st.text_input('Target House Number')
st.text_input('Target ZIP Code')
st.text_input('Target City')

#Buttons to select critical amenities the customers want around his flat
st.header('Select Amenities')

#create a dictionnary and assign user friendly amenities
amenity_config = {
    "Supermarket": "shop",
    "School": "amenity",
    "Hospital": "amenity",
    "Pharmacy": "amenity",
    "Restaurant": "amenity"
}

#create an empty list for user amenities
selected_amenities = []

#selection section for customer to choose
cols = st.columns(len(amenity_config))              #understand these features and cite
for i, label in enumerate(amenity_config.keys()):
    if cols[i].checkbox(label, key=f"btn_{label}"):
        selected_amenities.append(label.lower())

#set slider using streamlit features https://docs.streamlit.io/develop/api-reference/widgets/st.slider
radius = st.slider('Search Radius in meters', 0, 5000, 300)

#Search button using https://docs.streamlit.io/develop/api-reference/widgets/st.slider
st.button('Search nearby')
