import streamlit as st
import os, json, re, io
from urllib.error import URLError
import requests
from utilities.formrecognizer import analyze_read
from os import path
from utilities.azureblobstorage import upload_file, get_all_files
import zipfile

from utilities import utils, redisembeddings
import os

def add_embeddings(text):
    embeddings = utils.chunk_and_embed(text)
    # Store embeddings in Redis
    redisembeddings.set_document(embeddings)

    token_len = utils.get_token_count(text)
    if token_len >= 2046:
        st.warning(f'Your input text has {token_len} tokens. Please try reducing it (<= 2046) to get a full embeddings representation')


########## START - MAIN ##########
try:
    # Set page layout to wide screen and menu item
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App

	Document Reader Sample Demo.
	'''
    }
    st.set_page_config(layout="wide", menu_items=menu_items)

    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


    col1, col2, col3 = st.columns([2,1,1])

    files_data = get_all_files()

    st.dataframe(files_data)



except URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
        """
        % e.reason
    )

########## END - MAIN ##########
