import streamlit as st
from streamlit_chat import message
import streamlit.components.v1 as components
from utilities.helper import LLMHelper
import requests
import regex as re

def clear_chat_data():
    st.session_state['input'] = ""
    st.session_state['chat_history'] = []
    st.session_state['source_documents'] = []
    st.session_state['chat_context'] = []
    st.session_state['context_show_option'] = 'context within full source document'
    st.session_state['askedquestion'] = ''

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'source_documents' not in st.session_state:
    st.session_state['source_documents'] = []
if 'chat_context' not in st.session_state:
    st.session_state['chat_context'] = []

context_show_options = ('extracted context only', 'context within full source document')
if 'context_show_option' not in st.session_state:
    st.session_state['context_show_option'] = 'context within full source document'

llm_helper = LLMHelper()

if 'askedquestion' not in st.session_state:
    st.session_state.askedquestion = ''

def questionAsked():
    st.session_state.askedquestion = st.session_state.input

# Chat 
input_text = st.text_input("You: ", placeholder="type your question", key="input", on_change=questionAsked)
clear_chat = st.button("Clear chat", key="clear_chat", on_click=clear_chat_data)

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
        placeholder.empty()

    placeholder = st.empty()
    with placeholder:
        htmlcontent = html_content.format(filename=filename, text=text)
        components.html(htmlcontent, height=500)
    pass


if st.session_state.askedquestion:
    question = st.session_state.askedquestion
    st.session_state.askedquestion = ""
    question, result, context, sources = llm_helper.get_semantic_answer_lang_chain(question, st.session_state['chat_history'])
    st.session_state['chat_history'].append((question, result))
    st.session_state['source_documents'].append(sources)
    st.session_state['chat_context'].append(context)

          
if st.session_state['chat_history']:
    history_range = range(len(st.session_state['chat_history'])-1, -1, -1)
    for i in range(len(st.session_state['chat_history'])-1, -1, -1):
        # message(st.session_state['chat_history'][i][1], key=str(i))

        if i == history_range.start:

            st.session_state['context_show_option'] = st.selectbox(
                'Choose how to display context used to answer the question when clicking on a document source below:',
                context_show_options,
                index=context_show_options.index(st.session_state['context_show_option'])
            )

            answer_with_citations, sourceList, linkList, filenameList = llm_helper.get_links_filenames(st.session_state['chat_history'][i][1], st.session_state['source_documents'][i])
            st.session_state['chat_history'][i] = st.session_state['chat_history'][i][:1] + (answer_with_citations,)
            answer_with_citations = re.sub(r'\$\^\{(\d+)\}\$', r'(\1)', st.session_state['chat_history'][i][1]) # message() does not get Latex nor html
            message(answer_with_citations, key=str(i))

            for id in range(len(sourceList)):
                if st.button(f'({id+1}) {filenameList[id]}', key=filenameList[id]):
                    display_iframe(filenameList[id], linkList[id], st.session_state['chat_context'][i][sourceList[id]])

        else:
            st.markdown(f'\n\nSources: {st.session_state["source_documents"][i]}')
        message(st.session_state['chat_history'][i][0], is_user=True, key=str(i) + '_user')
