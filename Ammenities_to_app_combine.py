import streamlit as st

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
cols = st.columns(len(amenity_config))

