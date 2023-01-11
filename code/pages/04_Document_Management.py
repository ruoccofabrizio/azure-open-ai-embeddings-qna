import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils, redisembeddings
import os

def delete_row():
    st.session_state['data_to_drop'] 
    redisembeddings.delete_document(st.session_state['data_to_drop'])

try:
    # Set page layout to wide screen and menu item
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App
	 Embedding testing application.
	'''
    }
    st.set_page_config(layout="wide", menu_items=menu_items)

    # Query RediSearch to get all the embeddings
    data = redisembeddings.get_documents()

    if len(data) == 0:
        st.warning("No embeddings found. Go to the 'Add Document' tab to insert your docs.")
    else:
        data

        col1, col2, col3, col4 = st.columns([1,1,2,1])
        with col1:
            st.text("")
            st.text("")
            st.download_button("Download data", data.to_csv(index=False).encode('utf-8'), "embeddings.csv", "text/csv", key='download-embeddings')
        with col3:
            st.selectbox("Embedding id to delete", data.get('id',[]), key="data_to_drop")
        with col4:
            st.text("")
            st.text("")
            st.button("Delete row", on_click=delete_row)

except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )