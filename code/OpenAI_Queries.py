from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import traceback
from utilities.helper import LLMHelper

import logging
logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

def check_deployment():
    # Check if the deployment is working
    #\ 1. Check if the llm is working
    try:
        llm_helper = LLMHelper()
        llm_helper.llm("Generate a joke!")
        st.success("LLM is working!")
    except Exception as e:
        st.error(f"""LLM is not working. 
            Please check you have a deployment name {llm_helper.deployment_name} in your Azure OpenAI resource {llm_helper.api_base}.
            Then restart your application.
            """)
        st.error(traceback.format_exc())
    #\ 2. Check if the embedding is working
    try:
        llm_helper = LLMHelper()
        llm_helper.embeddings.embed_documents(texts=["This is a test"])
        st.success("Embedding is working!")
    except Exception as e:
        st.error(f"""Embedding model is not working. 
            Please check you have a deployment name {llm_helper.model} in your Azure OpenAI resource {llm_helper.api_base}.
            Then restart your application.
            """)
        st.error(traceback.format_exc())
    #\ 3. Check if the translation is working
    try:
        llm_helper = LLMHelper()
        llm_helper.translator.translate("This is a test", "it")
        st.success("Translation is working!")
    except Exception as e:
        st.error(f"""Translation model is not working. 
            Please check your Azure Translator key in the App Settings.
            Then restart your application.
            """)
        st.error(traceback.format_exc())
    #\ 4. Check if the Redis is working with previous version of data
    try:
        llm_helper = LLMHelper()
        if llm_helper.vector_store.check_existing_index("embeddings-index"):
            st.warning("""Seems like you're using a Redis with an old data structure.
            If you want to use the new data structure, you can start using the app and go to "Add Document" -> "Add documents in Batch" and click on "Convert all files and add embeddings" to reprocess your documents. 
            To remove this working, please delete the index "embeddings-index" from your Redis.
            If you prefer to use the old data structure, please change your Web App container image to point to the docker image: fruocco/oai-embeddings:2023-03-27_25. 
            """)
        else:
            st.success("Redis is working!")
    except Exception as e:
        st.error(f"""Redis is not working. 
            Please check your Redis connection string in the App Settings.
            Then restart your application.
            """)
        st.error(traceback.format_exc())


@st.cache_data()
def get_languages():
    return llm_helper.translator.get_available_languages()

try:

    default_prompt = "" 
    default_question = "" 
    default_answer = ""

    if 'question' not in st.session_state:
        st.session_state['question'] = default_question
    # if 'prompt' not in st.session_state:
    #     st.session_state['prompt'] = os.getenv("QUESTION_PROMPT", "Please reply to the question using only the information present in the text above. If you can't find it, reply 'Not in the text'.\nQuestion: _QUESTION_\nAnswer:").replace(r'\n', '\n')
    if 'response' not in st.session_state:
        st.session_state['response'] = default_answer
    if 'context' not in st.session_state:
        st.session_state['context'] = ""

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

    # Get available languages for translation
    available_languages = get_languages()

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.image(os.path.join('images','microsoft.png'))

    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        st.button("Check deployment", on_click=check_deployment)
    with col3:
        with st.expander("Settings"):
            # model = st.selectbox(
            #     "OpenAI GPT-3 Model",
            #     [os.environ['OPENAI_ENGINE']]
            # )
            # st.text_area("Prompt",height=100, key='prompt')
            # st.tokens_response = st.slider("Tokens response length", 100, 500, 400)
            # st.temperature = st.slider("Temperature", 0.0, 1.0, 0.1)
            st.selectbox("Language", [None] + list(available_languages.keys()), key='translation_language')

    question = st.text_input("OpenAI Semantic Answer", default_question)

    if question != '':
        st.session_state['question'] = question
        st.session_state['question'], st.session_state['response'], st.session_state['context'], sources = llm_helper.get_semantic_answer_lang_chain(question, [])
        st.markdown("Answer:" + st.session_state['response'])
        st.markdown(f'\n\nSources: {sources}') 
        with st.expander("Question and Answer Context"):
            st.markdown(st.session_state['context'].replace('$', '\$'))
            st.markdown(f"SOURCES: {sources}") 

    if st.session_state['translation_language'] and st.session_state['translation_language'] != '':
        st.write(f"Translation to other languages, 翻译成其他语言, النص باللغة العربية")
        st.write(f"{llm_helper.translator.translate(st.session_state['response'], available_languages[st.session_state['translation_language']])}")		
		
except Exception:
    st.error(traceback.format_exc())
