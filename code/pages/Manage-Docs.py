import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils
import os

def embeddings():
    embeddings = utils.chunk_and_embed(st.session_state['doc_text'])
    data = pd.read_csv(os.environ['embeddings_path'])
    data = data.to_dict('records')
    data.append(embeddings)
    data = pd.DataFrame(data)
    data.to_csv(os.environ['embeddings_path'], index=False)

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

    data = pd.read_csv(os.environ['embeddings_path'])

    st.session_state['doc_text'] = st.text_area("Add a new document", height=600)

    col1, col2, col3 = st.columns([1,1,1])

    with col3:
        st.session_state['embeddings_model'] = st.selectbox('Embeddings models', (os.environ['embeddings_engines'].split(',')))
        st.button("Compute Embeddings", on_click=embeddings)

    data

    col1, col2, col3 = st.columns([1,1,2])
    with col3:
        st.download_button("Download embeddings", data.to_csv(index=False).encode('utf-8'), "embeddings.csv", "text/csv", key='download-embeddings')


except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )