import streamlit as st
import os, json, re, io
from os import path
import requests
import mimetypes
import traceback
from utilities.helper import LLMHelper
import uuid
from redis.exceptions import ResponseError 

def upload_text_and_embeddings():
    file_name = f"{uuid.uuid4()}.txt"
    source_url = llm_helper.blob_client.upload_file(st.session_state['doc_text'], file_name=file_name, content_type='text/plain')
    llm_helper.add_embeddings_lc(source_url) 
    st.success("Embeddings added successfully.")

def remote_convert_files_and_add_embeddings(process_all=False):
    url = os.getenv('CONVERT_ADD_EMBEDDINGS_URL')
    if process_all:
        url = f"{url}?process_all=true"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            st.success(f"{response.text}\nPlease note this is an asynchronous process and may take a few minutes to complete.")
        else:
            st.error(f"Error: {response.text}")
    except Exception as e:
        st.error(traceback.format_exc())


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

    llm_helper = LLMHelper()

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
                st.session_state['file_url'] = llm_helper.blob_client.upload_file(bytes_data, st.session_state['filename'], content_type=content_type)

                converted_filename = ''
                if uploaded_file.name.endswith('.txt'):
                    # Add the text to the embeddings
                    llm_helper.add_embeddings_lc(st.session_state['file_url'])

                else:
                    # Get OCR with Layout API and then add embeddigns
                    converted_filename = llm_helper.convert_file_and_add_embeddings(st.session_state['file_url'], st.session_state['filename'], st.session_state['translate'])
                
                llm_helper.blob_client.upsert_blob_metadata(uploaded_file.name, {'converted': 'true', 'embeddings_added': 'true', 'converted_filename': converted_filename})
                st.success(f"File {uploaded_file.name} embeddings added to the knowledge base.")
            
            # pdf_display = f'<iframe src="{st.session_state["file_url"]}" width="700" height="1000" type="application/pdf"></iframe>'

    with st.expander("Add text to the knowledge base", expanded=False):
        col1, col2 = st.columns([3,1])
        with col1: 
            st.session_state['doc_text'] = st.text_area("Add a new text content and the click on 'Compute Embeddings'", height=600)

        with col2:
            st.session_state['embeddings_model'] = st.selectbox('Embeddings models', [llm_helper.get_embeddings_model()['doc']], disabled=True)
            st.button("Compute Embeddings", on_click=upload_text_and_embeddings)

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
                    st.session_state['file_url'] = llm_helper.blob_client.upload_file(bytes_data, st.session_state['filename'], content_type=content_type)
                    if up.name.endswith('.txt'):
                        # Add the text to the embeddings
                        llm_helper.blob_client.upsert_blob_metadata(up.name, {'converted': "true"})

        col1, col2, col3 = st.columns([2,2,2])
        with col1:
            st.button("Convert new files and add embeddings", on_click=remote_convert_files_and_add_embeddings)
        with col3:
            st.button("Convert all files and add embeddings", on_click=remote_convert_files_and_add_embeddings, args=(True,))

    with st.expander("View documents in the knowledge base", expanded=False):
        # Query RediSearch to get all the embeddings
        try:
            data = llm_helper.get_all_documents(k=1000)
            if len(data) == 0:
                st.warning("No embeddings found. Copy paste your data in the text input and click on 'Compute Embeddings' or drag-and-drop documents.")
            else:
                st.dataframe(data, use_container_width=True)
        except Exception as e:
            if isinstance(e, ResponseError):
                st.warning("No embeddings found. Copy paste your data in the text input and click on 'Compute Embeddings' or drag-and-drop documents.")
            else:
                st.error(traceback.format_exc())


except Exception as e:
    st.error(traceback.format_exc())
