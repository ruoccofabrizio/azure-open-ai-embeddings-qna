from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import streamlit.components.v1 as components
import os
import traceback
from utilities.helper import LLMHelper

import requests
import regex as re

import logging
logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

def check_deployment():
    # Check if the deployment is working
    #\ 1. Check if the llm is working
    try:
        llm_helper = LLMHelper()
        llm_helper.get_completion("Generate a joke!")
        st.success("LLM is working!")
    except Exception as e:
        st.error(f"""LLM is not working.  
            Please check you have a deployment name {llm_helper.deployment_name} in your Azure OpenAI resource {llm_helper.api_base}.  
            If you are using an Instructions based deployment (text-davinci-003), please check you have an environment variable OPENAI_DEPLOYMENT_TYPE=Text or delete the environment variable OPENAI_DEPLOYMENT_TYPE.  
            If you are using a Chat based deployment (gpt-35-turbo or gpt-4-32k or gpt-4), please check you have an environment variable OPENAI_DEPLOYMENT_TYPE=Chat.  
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
            Please check you have a deployment named "text-embedding-ada-002" for "text-embedding-ada-002" model in your Azure OpenAI resource {llm_helper.api_base}.  
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


def ChangeButtonStyle(wgt_txt, wch_hex_colour = '#000000', wch_border_style = ''):
    htmlstr = """<script>var elements = window.parent.document.querySelectorAll('*'), i;
                    str_wgt_txt = '{wgt_txt}'
                    str_wgt_txt = str_wgt_txt.replace("/(^|[^\\])'/g", "$1\\'");
                    for (i = 0; i < elements.length; ++i)
                    {{ if (elements[i].innerText == str_wgt_txt) 
                        {{
                            elements[i].style.color  = '{wch_hex_colour}';
                            let border_style = '{wch_border_style}';
                            if (border_style.length > 0) {{
                                elements[i].style.border ='{wch_border_style}';
                                }}
                        }} }}</script>  """

    htmlstr = htmlstr.format(wgt_txt=wgt_txt, wch_hex_colour=wch_hex_colour, wch_border_style=wch_border_style)
    components.html(f"{htmlstr}", height=0, width=0)

@st.cache_data()
def get_languages():
    return llm_helper.translator.get_available_languages()

try:

    default_prompt = "" 
    default_question = "" 
    default_answer = ""


    if 'question' not in st.session_state:
        st.session_state['question'] = default_question
    if 'response' not in st.session_state:
        st.session_state['response'] = default_answer
    if 'context' not in st.session_state:
        st.session_state['context'] = ""
    if 'sources' not in st.session_state:
        st.session_state['sources'] = ""
    if 'followup_questions' not in st.session_state:
        st.session_state['followup_questions'] = []
    if 'input_message_key' not in st.session_state:
        st.session_state ['input_message_key'] = 1
    if 'do_not_process_question' not in st.session_state:
        st.session_state['do_not_process_question'] = False

    if 'askedquestion' not in st.session_state:
        st.session_state.askedquestion = default_question

    if 'context_show_option' not in st.session_state:
        st.session_state['context_show_option'] = 'context within full source document'


    if 'tab_context' not in st.session_state:
        st.session_state['tab_context'] = 'Not opened yet'
    else:
        if st.session_state['question'] != '' and st.session_state['tab_context'] != 'Not opened yet' and st.session_state['tab_context'] != 'Chat':
            st.session_state['tab_context'] = 'Open_Queries'

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
        ChangeButtonStyle("Check deployment", "#885555")
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

    # Callback to display document sources
    def show_document_source(filename, link, contextList):
        st.session_state['do_not_process_question'] = True
        display_iframe(filename, link, contextList)

    # Callback to assign the follow-up question is selected by the user
    def ask_followup_question(followup_question):
        st.session_state.askedquestion = followup_question
        st.session_state['input_message_key'] = st.session_state['input_message_key'] + 1

    def questionAsked():
        st.session_state.askedquestion = st.session_state["input"+str(st.session_state ['input_message_key'])]

    question = st.text_input("Azure OpenAI Semantic Answer", value=st.session_state['askedquestion'], key="input"+str(st.session_state ['input_message_key']), on_change=questionAsked)

    # Display the context(s) associated with a source document used to andwer, with automaic scroll to the yellow highlighted context
    def display_iframe(filename, link, contextList):
        st.session_state['do_not_process_question'] = True
        st.session_state['askedquestion'] = st.session_state.question
        if st.session_state['context_show_option'] == 'context within full source document':
            try:
                response = requests.get(link)
                text = response.text
                text = llm_helper.clean_encoding(text)
                for i, context in enumerate(contextList):
                    context = llm_helper.clean_encoding(context)
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

        def close_iframe():
            placeholder.empty()
            st.session_state['do_not_process_question'] = True

        st.button("Close", on_click=close_iframe)
        
        placeholder = st.empty()
        with placeholder:
            htmlcontent = html_content.format(filename=filename, text=text)
            components.html(htmlcontent, height=500)

        pass

    if st.session_state['tab_context'] != 'Open_Queries' and st.session_state['question'] != '' and st.session_state['question'] != st.session_state['followup_questions']:
        st.session_state['tab_context'] = 'Open_Queries'
        st.session_state['do_not_process_question'] = True
        ask_followup_question(st.session_state['question'])

    # Answer the question if any
    if st.session_state.askedquestion != '' and st.session_state['do_not_process_question'] != True:
        st.session_state['question'] = st.session_state.askedquestion
        st.session_state.askedquestion = ""
        st.session_state['question'], \
        st.session_state['response'], \
        st.session_state['context'], \
        st.session_state['sources'] = llm_helper.get_semantic_answer_lang_chain(st.session_state['question'], [])
        st.session_state['response'], followup_questions_list = llm_helper.extract_followupquestions(st.session_state['response'])
        st.session_state['followup_questions'] = followup_questions_list
        st.session_state['response'] = llm_helper.clean_encoding(st.session_state['response'])
        st.session_state['context'] = llm_helper.clean_encoding(st.session_state['context'])

    st.session_state['do_not_process_question'] = False
    sourceList = []


    # Display the sources and context - even if the page is reloaded
    if st.session_state['sources'] or st.session_state['context']:
        st.session_state['response'], sourceList, matchedSourcesList, linkList, filenameList = llm_helper.get_links_filenames(st.session_state['response'], st.session_state['sources'])
        st.markdown("**Answer:**" + st.session_state['response'])
 
    # Display proposed follow-up questions which can be clicked on to ask that question automatically
    if len(st.session_state['followup_questions']) > 0:
        st.markdown('**Proposed follow-up questions:**')
    with st.container():
        for questionId, followup_question in enumerate(st.session_state['followup_questions']):
            if followup_question:
                str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)
                st.button(str_followup_question, key=1000+questionId, on_click=ask_followup_question, args=(followup_question, ))

    if st.session_state['sources'] or st.session_state['context']:
        # Buttons to display the context used to answer
        st.markdown('**Document sources:**')
        for id in range(len(sourceList)):
            st.button(f'({id+1}) {filenameList[id]}', key=filenameList[id], on_click=show_document_source, args=(filenameList[id], linkList[id], st.session_state['context'][sourceList[id]], ))

        # Details on the question and answer context
        with st.expander("Question and Answer Context"):
            if not st.session_state['context'] is None and st.session_state['context'] != []:
                for content_source in st.session_state['context'].keys():
                    st.markdown(f"#### {content_source}")
                    for context_text in st.session_state['context'][content_source]:
                        context_text = llm_helper.clean_encoding(context_text)
                        st.markdown(f"{context_text}")

            st.markdown(f"SOURCES: {st.session_state['sources']}") 

    # Source Buttons Styles
    for id in range(len(sourceList)):
        if filenameList[id] in matchedSourcesList:
            ChangeButtonStyle(f'({id+1}) {filenameList[id]}', "#228822", wch_border_style='none')
        else:
            ChangeButtonStyle(f'({id+1}) {filenameList[id]}', "#AAAAAA", wch_border_style='none')

    for questionId, followup_question in enumerate(st.session_state['followup_questions']):
        if followup_question:
            str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)
            ChangeButtonStyle(str_followup_question, "#5555FF", wch_border_style='none')

    if st.session_state['translation_language'] and st.session_state['translation_language'] != '':
        st.write(f"Translation to other languages, 翻译成其他语言, النص باللغة العربية")
        st.write(f"{llm_helper.translator.translate(st.session_state['response'], available_languages[st.session_state['translation_language']])}")		
		
except Exception:
    st.error(traceback.format_exc())
