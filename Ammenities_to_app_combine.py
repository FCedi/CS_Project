import streamlit as st

#set page title using https://docs.streamlit.io/ examples
st.set_page_config(page_title='Local Amenities Finder', layout='centered')
st.title('Local Amenities :red[Finder]')

#adress input section using https://docs.streamlit.io/ examples
st.header('Enter Your Address')
col1, col2 = st.columns([2, 1])
col1.text_input('Street')
col2.text_input('House Number')
st.text_input("ZIP Code", "9000")
st.text_input("City", "St. Gallen")
