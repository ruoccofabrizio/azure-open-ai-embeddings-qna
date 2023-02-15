import streamlit as st
from urllib.error import URLError
import pandas as pd
import os, json, re, io
from os import path
import zipfile
from utilities import utils, redisembeddings
from utilities.formrecognizer import analyze_read
from utilities.azureblobstorage import upload_file, get_all_files, upsert_blob_metadata
from utilities.translator import translate
from utilities.utils import add_embeddings, convert_file_and_add_embeddings
import requests
import mimetypes

def embeddings():
    embeddings = utils.chunk_and_embed(st.session_state['doc_text'])
    # Store embeddings in Redis
    redisembeddings.set_document(embeddings)

    # Get token count
    token_len = utils.get_token_count(st.session_state['doc_text'])
    if token_len >= 3000:
        st.warning(f'Your input text has {token_len} tokens. Please try reducing it (<= 3000) to get a full embeddings representation')


def remote_convert_files_and_add_embeddings():
    response = requests.post(os.getenv('CONVERT_ADD_EMBEDDINGS_URL'))
    if response.status_code == 200:
        st.success(f"{response.text}\nPlease note this is an asynchronous process and may take a few minutes to complete.")

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

    with st.expander("Add a single document to the knowledge base", expanded=True):
        st.write("For heavy or long PDF, please use the 'Add documents in batch' option below.")
        st.checkbox("Translate document to English", key="translate")
        uploaded_file = st.file_uploader("Upload a document to add it to the knowledge base", type=['pdf','jpeg','jpg','png', 'txt'])
        if uploaded_file is not None:
            # To read file as bytes:
            bytes_data = uploaded_file.getvalue()

            if st.session_state.get('filename', '') != uploaded_file.name:
                # Upload a new file
                st.session_state['filename'] = uploaded_file.name
                content_type = mimetypes.MimeTypes().guess_type(uploaded_file.name)[0]
                st.session_state['file_url'] = upload_file(bytes_data, st.session_state['filename'], content_type=content_type)

                if uploaded_file.name.endswith('.txt'):
                    # Add the text to the embeddings
                    add_embeddings(uploaded_file.read().decode('utf-8'), uploaded_file.name, os.getenv('OPENAI_EMBEDDINGS_ENGINE_DOC', 'text-embedding-ada-002'))

                else:
                    # Get OCR with Layout API
                    convert_file_and_add_embeddings(st.session_state['file_url'], st.session_state['filename'], st.session_state['translate'])
                
                upsert_blob_metadata(uploaded_file.name, {'converted': 'true', 'embeddings_added': 'true'})
                st.success(f"File {uploaded_file.name} embeddings added to the knowledge base.")
            
            # pdf_display = f'<iframe src="{st.session_state["file_url"]}" width="700" height="1000" type="application/pdf"></iframe>'

    with st.expander("Add text to the knowledge base", expanded=False):
        col1, col2 = st.columns([3,1])
        with col1: 
            st.session_state['doc_text'] = st.text_area("Add a new text content and the click on 'Compute Embeddings'", height=600)

        with col2:
            st.session_state['embeddings_model'] = st.selectbox('Embeddings models', [utils.get_embeddings_model()['doc']], disabled=True)
            st.button("Compute Embeddings", on_click=embeddings)

    with st.expander("Add documents in Batch", expanded=False):
        uploaded_files = st.file_uploader("Upload a document to add it to the Azure Storage Account", type=['pdf','jpeg','jpg','png', 'txt'], accept_multiple_files=True)
        if uploaded_files is not None:
            for up in uploaded_files:
                # To read file as bytes:
                bytes_data = up.getvalue()

                if st.session_state.get('filename', '') != up.name:
                    # Upload a new file
                    st.session_state['filename'] = up.name
                    content_type = mimetypes.MimeTypes().guess_type(up.name)[0]
                    st.session_state['file_url'] = upload_file(bytes_data, st.session_state['filename'], content_type=content_type)
                    if up.name.endswith('.txt'):
                        # Add the text to the embeddings
                        upsert_blob_metadata(up.name, {'converted': "true"})

        st.button("Convert all files and add embeddings", on_click=remote_convert_files_and_add_embeddings)


    with st.expander("View documents in the knowledge base", expanded=False):
        # Query RediSearch to get all the embeddings
        data = redisembeddings.get_documents()
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