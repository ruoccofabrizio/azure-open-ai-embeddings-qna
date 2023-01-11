import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils, redisembeddings
import os

def embeddings():
    embeddings = utils.chunk_and_embed(st.session_state['doc_text'])
    # Store embeddings in Redis
    print(embeddings.keys())
    redisembeddings.set_document(embeddings)


    token_len = utils.get_token_count(st.session_state['doc_text'])
    if token_len >= 2046:
        st.warning(f'Your input text has {token_len} tokens. Please try reducing it (<= 2046) to get a full embeddings representation')

def delete_row():
    st.session_state['data_to_drop'] 
    redisembeddings.delete_document(st.session_state['data_to_drop'])

def token_count():
    st.session_state['token_count'] = utils.get_token_count(st.session_state['doc_text'])

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

    st.session_state['doc_text'] = st.text_area("Add a new document", height=600)

    col1, col2, col3 = st.columns([1,1,1])

    with col3:
        st.session_state['embeddings_model'] = st.selectbox('Embeddings models', (os.environ['embeddings_engines'].split(',')))
        st.button("Compute Embeddings", on_click=embeddings)

    if len(data) == 0:
        st.warning("No embeddings found. Copy paste your data in the text input and click on 'Compute Embeddings'.")
    else:
        data


except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )