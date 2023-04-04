from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import streamlit.components.v1 as components
import os
import traceback
from utilities.helper import LLMHelper

import requests

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
    if 'sources' not in st.session_state:
        st.session_state['sources'] = ""

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

    if 'askedquestion' not in st.session_state:
        st.session_state.askedquestion = ''

    def questionAsked():
        st.session_state.askedquestion = st.session_state.inputquestion

    question = st.text_input("OpenAI Semantic Answer", default_question, key='inputquestion', on_change=questionAsked)

    def display_iframe(filename, link, contextList):
        if st.session_state['context_show_option'] == 'context within full source document':
            try:
                response = requests.get(link)
                text = response.text
                for i, context in enumerate(contextList):
                    contextSpan = f" <span id='ContextTag{i}' style='background-color: yellow'><b>{context}</b></span>"
                    text = text.replace(context, contextSpan)
                text = text.replace('\n', '<br><br>')

            except Exception as e:
                text = "Could not load the document source content"
        else:
            text = ""
            for context in contextList:
                text = text + context.replace('\n', '<br><br>') + '<br>'

        html_content = """
        <!DOCTYPE html>
        <head>
        <script>
            window.onload = function() {{
            setTimeout(function() {{
                // Code to execute after 0.5 seconds
                var iframe = this.document.getElementById('{filename}');
                var element = iframe.contentDocument.getElementById('ContextTag0');
                if (element !== null) {{
                    element.scrollIntoView({{
                    behavior: 'smooth',
                    }});
                }}
            }}, 500);
            }};
        </script>
        </head>
        <body>
            <div>
            <iframe id="{filename}" srcdoc="{text}" width="100%" height="480px"></iframe>
            </div>
        </body>
        """

        if st.button("Close"):
            st.placeholder.empty()

        placeholder = st.empty()
        with placeholder:
            # htmlcontent = html_content.format(link=link, filename=filename)
            htmlcontent = html_content.format(filename=filename, text=text)
            components.html(htmlcontent, height=500)
        pass


    if 'context_show_option' not in st.session_state:
        st.session_state['context_show_option'] = 'context within full source document'

    # Answer the question if any
    if st.session_state.askedquestion != '':
        st.session_state['question'] = st.session_state.askedquestion
        st.session_state.askedquestion = ""
        st.session_state['question'], st.session_state['response'], st.session_state['context'], st.session_state['sources'] = llm_helper.get_semantic_answer_lang_chain(st.session_state['question'], [])

    # Display the sources and context - even if the page is reloaded
    if st.session_state['sources'] or st.session_state['context']:
        st.markdown("Answer:" + st.session_state['response'])
        # st.markdown(f'\n\nSources: {sources}')
        split_sources = st.session_state['sources'].split('  \n ')
        for src in split_sources:
            if src != '':
                link = src[1:].split('(')[1][:-1].split(')')[0]
                filename = src[1:].split(']')[0]
                if st.button(filename, key=filename):
                    context = st.session_state['context']
                    display_iframe(filename, link, st.session_state['context'][src])
        with st.expander("Question and Answer Context"):
            if not st.session_state['context'] is None and st.session_state['context'] != []:
                for content_source in st.session_state['context'].keys():
                    st.markdown(f"#### {content_source}")
                    for context_text in st.session_state['context'][content_source]:
                        st.markdown(f"{context_text}")
            
            # theContext = llm_helper.filter_sourcesLinks(st.session_state['context'].replace('$', '\$'))
            # st.markdown(theContext)
            st.markdown(f"SOURCES: {st.session_state['sources']}") 

    if st.session_state['translation_language'] and st.session_state['translation_language'] != '':
        st.write(f"Translation to other languages, 翻译成其他语言, النص باللغة العربية")
        st.write(f"{llm_helper.translator.translate(st.session_state['response'], available_languages[st.session_state['translation_language']])}")		
		
except Exception:
    st.error(traceback.format_exc())
