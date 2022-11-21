import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils
import os

df = utils.initialize(embeddings_path=os.environ['embeddings_path'], engine='davinci')

try:

    default_prompt = pd.read_csv(os.environ['embeddings_path'])['text'][0].encode('utf-8').decode('utf-8')
    default_question = "posso effettuare bonifici esteri con la postepay evolution?"
    default_answer = "Sì, è possibile effettuare bonifici esteri con la Postepay Evolution. Per ricevere i bonifici SEPA da paesi diversi dall’Italia sarà necessario comunicare anche il codice BIC di Postepay S.p.A. PPAYITR1XXX"

    if 'question' not in st.session_state:
        st.session_state['question'] = default_question
    if 'prompt' not in st.session_state:
        st.session_state['prompt'] = default_prompt        
    if 'response' not in st.session_state:
        st.session_state['response'] = {
            "choices" :[{
                "text" : default_answer
            }]
        }    
    
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

    col1, col2, col3 = st.columns([2,2,1])
    with col3:
        model = st.selectbox(
            "OpenAI GPT-3 Model",
            (os.environ['engines'].split(','))
        )

    # col1, col2, col3, col4 = st.columns([9,1,5,1])
    # with col1:
    question = st.text_input("OpenAI Semantic Answer", default_question)

    if question != '':
        if question != st.session_state['question']:
            st.session_state['question'] = question
            st.session_state['prompt'], st.session_state['response'] = utils.get_semantic_answer(df, question, model=model, engine='davinci')
            st.write(f"Q: {question}")  
            st.write(st.session_state['response']['choices'][0]['text'])
            with st.expander("Question and Answer Context"):
                st.text(st.session_state['prompt'])
        else:
            st.write(f"Q: {st.session_state['question']}")  
            st.write(f"{st.session_state['response']['choices'][0]['text']}")
            with st.expander("Question and Answer Context"):
                st.text(st.session_state['prompt'].encode().decode())

except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )