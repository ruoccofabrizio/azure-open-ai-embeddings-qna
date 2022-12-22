import streamlit as st
import os, json, re
from urllib.error import URLError
import requests
from utilities.formrecognizer import analyze_read
from os import path
from utilities.azureblobstorage import upload_file, get_all_files

def convert_file(fullpath, filename):
    # Extract the text from the file
    text = analyze_read(fullpath)
    # Upload the text to Azure Blob Storage
    upload_file(text, f'converted/{filename}.txt', 'application/text')

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


    uploaded_file = st.file_uploader("Upload a document", type=['pdf'])
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()

        if st.session_state.get('filename', '') != uploaded_file.name:
            # Upload a new file
            st.session_state['filename'] = uploaded_file.name
            st.session_state['file_url'] = upload_file(bytes_data, st.session_state['filename'])
            # Get OCR with Read API
            st.session_state['text'] = analyze_read(st.session_state['file_url'])
        
        pdf_display = f'<iframe src="{st.session_state["file_url"]}" width="700" height="1000" type="application/pdf"></iframe>'

    col1, col2, col3 = st.columns([2,1,1])

    files_data = get_all_files()

    cols = st.columns([2,2,1])
    cols[0].write('Original File')
    cols[1].write('Converted File')
    cols[2].write('Convert')

    for x in files_data:
        col1, col2, col3,  = st.columns([2,2,1])
        col1.write(f'<a href="{x["fullpath"]}">{x["filename"]}</a>', unsafe_allow_html=True)
        if x['converted_path'] != '':
            col2.write(f'<a href="{x["converted_path"]}">{x["filename"]}.txt</a>', unsafe_allow_html=True)
        if not x['converted']:
            col3.button('Convert', key=x['filename']+'_button', on_click=convert_file, args= (x['fullpath'],x['filename'],))


except URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
        """
        % e.reason
    )

########## END - MAIN ##########
