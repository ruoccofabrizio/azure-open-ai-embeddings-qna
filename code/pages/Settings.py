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

    api_base = os.getenv('OpenAI_api_base', '')
    os.environ['OpenAI_api_base'] = st.text_input("OpenAI Resource", value=api_base)
    api_key = os.getenv("OpenAI_api_key", '')
    os.environ['OpenAI_api_key'] = st.text_input("OpenAI Key", value=api_key, type='password')
    engines = os.getenv('OpenAI_engines','')
    os.environ['OpenAI_engines'] = st.text_input("OpenAI Engine deployed", value=engines, disabled=True)
    st.session_state['limit_response'] = st.checkbox("Limit response to the provided text", value=st.session_state['limit_response'])


except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )