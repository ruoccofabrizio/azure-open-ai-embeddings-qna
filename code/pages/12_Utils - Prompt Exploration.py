import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils, redisembeddings
import os

def get_prompt():
    return f"{st.session_state['doc_text']}\n{st.session_state['input_prompt']}"
   
def customcompletion():
    _, response = utils.get_completion(get_prompt(), max_tokens=1000, model=os.getenv('OPENAI_ENGINES', 'text-davinci-003'))
    st.session_state['result'] = response['choices'][0]['text'].encode().decode()

def process_all(data):
    for doc in data.to_dict('records')[0:st.session_state['num_docs']]:
        print(doc['text'])
        prompt = f"{doc['text']}\n{st.session_state['input_prompt']}"
        _, response = utils.get_completion(prompt, max_tokens=1000, model=os.getenv('OPENAI_ENGINES', 'text-davinci-003'))
        redisembeddings.add_prompt_result(doc['id'], response['choices'][0]['text'].encode().decode(), doc['filename'], st.session_state['input_prompt'])
    st.session_state['data_processed'] = redisembeddings.get_prompt_results().to_csv(index=False)

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

    if not 'data_processed' in st.session_state:
        st.session_state['data_processed'] = None

    # Query RediSearch to get all the embeddings
    data = redisembeddings.get_documents()

    if len(data) == 0:
        st.warning("No embeddings found. Go to the 'Add Document' tab to insert your docs.")
    else:
        data

        # displaying a box for a custom prompt
        st.text_area(label="Document", height=400, key="doc_text")
        st.text_area(label="Prompt", height=100, key="input_prompt")
        st.button(label="Execute tasks", on_click=customcompletion)
        # displaying the summary
        result = ""
        if 'result' in st.session_state:
            result = st.session_state['result']
            st.text_area(label="Result", value=result, height=400)

        cols = st.columns([1,1,1,2])
        with cols[0]:
            st.number_input("Number of docs to process", value=10 if len(data) > 10 else len(data), min_value=1, max_value=len(data), key="num_docs")
        with cols[1]:
            st.text("-")
            st.button("Execute task on docs", on_click=process_all, args=(data,)) 
        with cols[2]:
            st.text("-")
            download_data = st.session_state['data_processed'] if st.session_state['data_processed'] is not None else ""
            st.download_button(label="Download results", data=download_data, file_name="results.csv", mime="text/csv", disabled=st.session_state['data_processed'] is None)


except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
