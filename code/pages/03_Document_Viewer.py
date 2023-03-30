import streamlit as st
import os
import traceback
from utilities.helper import LLMHelper

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

    llm_helper = LLMHelper()

    col1, col2, col3 = st.columns([2,1,1])

    files_data = llm_helper.blob_client.get_all_files()

    st.dataframe(files_data, use_container_width=True)

except Exception as e:
    st.error(traceback.format_exc())
