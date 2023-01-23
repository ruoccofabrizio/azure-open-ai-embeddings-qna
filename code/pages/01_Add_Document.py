import streamlit as st
from urllib.error import URLError
import pandas as pd
import os, json, re, io
from os import path
import zipfile
from utilities import utils, redisembeddings
from utilities.formrecognizer import analyze_read
from utilities.azureblobstorage import upload_file, get_all_files
from utilities.translator import translate

def embeddings():
    embeddings = utils.chunk_and_embed(st.session_state['doc_text'])
    # Store embeddings in Redis
    print(embeddings.keys())
    redisembeddings.set_document(embeddings)


    token_len = utils.get_token_count(st.session_state['doc_text'])
    if token_len >= 2046:
        st.warning(f'Your input text has {token_len} tokens. Please try reducing it (<= 2046) to get a full embeddings representation')

def add_embeddings(text):
    embeddings = utils.chunk_and_embed(text)
    # Store embeddings in Redis
    redisembeddings.set_document(embeddings)

def convert_file(fullpath, filename):
    # Extract the text from the file
    text = analyze_read(fullpath)
    # Upload the text to Azure Blob Storage
    zip_file = io.BytesIO()
    if st.session_state.translate:
        text = list(map(lambda x: translate(x), text))
    for k, v in enumerate(text):
        v = translate(v)
        with zipfile.ZipFile(zip_file, mode="a") as archive:
            archive.writestr(f"{k}.txt", v)
    upload_file(zip_file.getvalue(), f"converted/{filename}.zip", content_type='application/zip')
    for t in text:
        add_embeddings(t)

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

    with st.expander("Add documents to the knowledge base", expanded=True):
        st.checkbox("Translate document to English", key="translate")
        uploaded_file = st.file_uploader("Upload a document to add it to the knowledge base", type=['pdf','jpeg','jpg','png','doc','docx'])
        if uploaded_file is not None:
            # To read file as bytes:
            bytes_data = uploaded_file.getvalue()

            if st.session_state.get('filename', '') != uploaded_file.name:
                # Upload a new file
                st.session_state['filename'] = uploaded_file.name
                st.session_state['file_url'] = upload_file(bytes_data, st.session_state['filename'])
                # # Get OCR with Layout API
                convert_file(st.session_state['file_url'], st.session_state['filename'])
            
            # pdf_display = f'<iframe src="{st.session_state["file_url"]}" width="700" height="1000" type="application/pdf"></iframe>'


        col1, col2 = st.columns([3,1])
        with col1: 
            st.session_state['doc_text'] = st.text_area(" or Add a new text content and the click on 'Compute Embeddings'", height=600)

        with col2:
            st.session_state['embeddings_model'] = st.selectbox('Embeddings models', (os.environ['OPENAI_EMBEDDINGS_ENGINE_DOC'].split(',')))
            st.button("Compute Embeddings", on_click=embeddings)

    with st.expander("View documents in the knowledge base", expanded=False):
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