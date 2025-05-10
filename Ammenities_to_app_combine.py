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
street = col1.text_input('Street')
house_number = col2.text_input('House Number')
zip_code = st.text_input("ZIP Code")
city = st.text_input("City")

#Input section : Potential precise location customer want to measure distance to, again https://docs.streamlit.io/
st.header('Add a Target Location to Assess Distance')
target_street = st.text_input('Target Street')
target_house_number = st.text_input('Target House Number')
target_zip_code = st.text_input('Target ZIP Code')
target_city = st.text_input('Target City')

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
#assigning function to button
if st.button('Search nearby'):
    geolocator = Nominatim(user_agent="streamlit_app") #creating geocoder from geopy https://geopy.readthedocs.io/en/stable/index.html?highlight=user_agent
    full_address = f"{street} {house_number}, {zip_code} {city}" #Combines the address components the user entered into one full string
    location = geolocator.geocode(full_address)

    if not location:
        st.error('Location not found')
        st.session_state.map_html = None  #if adress not found, no map and error message
    else:
        lat, lon = location.latitude, location.longitude
        st.success(f"Found: {location.address} ({lat:.5f}, {lon:.5f})") #if found assign geoloc values

        folium_map = folium.Map(location=[lat, lon], zoom_start=14)
        folium.Marker(
            [lat, lon],
            tooltip='Your Location',
            icon=folium.Icon(color='blue')
        ).add_to(folium_map) #add features found to the map

        #attempt to add amenities using try/except block to handle errors
    try:
        for amenity in selected_amenities: #for funtion iterates dictionnary established before
            tag_type = amenity_config[amenity.capitalize()] #we assigned categories in the dictionnary before to certain tags, it assigns to proper openstreemap cat.
            query = f"""
            [out:json];
            (
                node["{tag_type}"="{amenity}"](around:{radius},{lat},{lon});
                way["{tag_type}"="{amenity}"](around:{radius},{lat},{lon});
                relation["{tag_type}"="{amenity}"](around:{radius},{lat},{lon}); #building the query for overpass in json to then be used in openstreetmap
            );
            out center;
            """
            response = requests.post("https://overpass-api.de/api/interpreter", data=query, timeout=30) #sends the query to overpas api, max 30 sec waiting time
            data = response.json() #response in a dictionnary
            elements = data.get("elements", []) #exctracts nodes ways and relations returned by overpass
#basically this block builds the overpass query

#processing data return by overpass
            results = [] #initializing a list to hold result
            for el in elements:
                    el_lat = el.get("lat") or el.get("center", {}).get("lat")
                    el_lon = el.get("lon") or el.get("center", {}).get("lon") #nods have long and lat directly, ways or relations have center dictionary, hence or function
                    if el_lat and el_lon:
                        dist = geodesic((lat, lon), (el_lat, el_lon)).meters #calculating distance in straight line
                        name = el.get("tags", {}).get("name", f"{amenity.title()} (Unnamed)") #extracting name
                        results.append((name, dist, el_lat, el_lon)) #creating complete list

            for name, dist, el_lat, el_lon in sorted(results, key=lambda x: x[1])[:4]:
                    folium.Marker(
                        [el_lat, el_lon],
                        tooltip=f"{name} — {dist:.0f} m",
                        icon=folium.Icon(color="green")
                    ).add_to(folium_map)
    except Exception as e:
        st.error(f'Error during Overpass request: {e}')
    #first attempt displaying map
    st.session_state.map_html = folium_map._repr_html_()
    


