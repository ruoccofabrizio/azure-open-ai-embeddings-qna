import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils
import os

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

    api_base = os.getenv('api_base', '')
    os.environ['api_base'] = st.text_input("OpenAI Resource", value=api_base)
    api_key = os.getenv("api_key", '')
    os.environ['api_key'] = st.text_input("OpenAI Key", value=api_key, type='password')
    engines = os.getenv('engines','')
    os.environ['engines'] = st.text_input("OpenAI Engine deployed", value=engines, disabled=True)
    embeddings_path = os.getenv('embeddings_path', '')
    os.environ['embeddings_path'] = st.text_input("Local embeddings path", value=embeddings_path)
    st.session_state['limit_response'] = st.checkbox("Limit response to the provided text", value=st.session_state['limit_response'])


except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )