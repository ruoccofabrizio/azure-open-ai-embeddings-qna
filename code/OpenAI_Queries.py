from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils, translator
import os, re

df = utils.initialize(engine='davinci')

@st.cache(suppress_st_warning=True)
def get_languages():
    return translator.get_available_languages()

try:

    default_prompt = "" 
    default_question = "" 
    default_answer = ""

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
    if 'limit_response' not in st.session_state:
        st.session_state['limit_response'] = True

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

    # Get available languages for translation
    available_languages = get_languages()

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.image(os.path.join('images','microsoft.png'))

    col1, col2, col3 = st.columns([2,2,2])
    with col3:
        with st.expander("Settings"):
            model = st.selectbox(
                "OpenAI GPT-3 Model",
                (os.environ['OPENAI_ENGINES'].split(','))
            )
            st.tokens_response = st.slider("Tokens response length", 100, 500, 400)
            st.temperature = st.slider("Temperature", 0.0, 1.0, 0.1)
            st.selectbox("Language", [None] + list(available_languages.keys()), key='translation_language')
            st.session_state['preprompt'] = st.text_input("Prompt to preapply", value='Please reply to the question using only the information present in the text above. If you can\'t find it, reply \'Answer not found within the knowledge base docs\'')


    question = st.text_input("OpenAI Semantic Answer", default_question)

    if question != '':
        if question != st.session_state['question']:
            st.session_state['question'] = question
            preprompt=st.session_state['preprompt']
            st.session_state['prompt'], st.session_state['response'] = utils.get_semantic_answer(df, question, model=model, engine='davinci', limit_response=st.session_state['limit_response'], tokens_response=st.tokens_response, temperature=st.temperature, preprompt=preprompt)
            st.write(f"Q: {question}")  
            reply= st.session_state['response']['choices'][0]['text']
            #formatting correctly for st
            if bool(re.search(r'%€$£^', reply)):
                st.latex(reply)
            else:    
                st.write(reply)
            with st.expander("Question and Answer Context"):
                st.text(st.session_state['prompt'])
        else:
            st.write(f"Q: {st.session_state['question']}")  
            reply= st.session_state['response']['choices'][0]['text']
            if bool(re.search(r'%€$£^', reply)):
                st.latex(reply)
            else:    
                st.write(reply)
            with st.expander("Question and Answer Context"):
                st.text(st.session_state['prompt'].encode().decode())

    if st.session_state['translation_language'] is not None:
        st.write(f"Translation to other languages, 翻译成其他语言, النص باللغة العربية")
        st.write(f"{translator.translate(st.session_state['response']['choices'][0]['text'], available_languages[st.session_state['translation_language']])}")		
		
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
