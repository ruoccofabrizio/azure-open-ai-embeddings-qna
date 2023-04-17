import streamlit as st
from streamlit_chat import message
import streamlit.components.v1 as components
from utilities.helper import LLMHelper
import requests
import regex as re
import os

def clear_chat_data():
    st.session_state['chat_history'] = []
    st.session_state['chat_source_documents'] = []
    st.session_state['chat_context'] = []
    st.session_state['chat_context_show_option'] = 'context within full source document'
    st.session_state['chat_askedquestion'] = ''
    st.session_state['chat_question'] = ''
    st.session_state['chat_followup_questions'] = []
    st.session_state['do_not_process_question'] = False
    st.session_state['tab_context'] = 'Not opened yet'
    answer_with_citations = ""


# Initialize chat history
if 'chat_question' not in st.session_state:
        st.session_state['chat_question'] = ''
if 'chat_askedquestion' not in st.session_state:
    st.session_state.chat_askedquestion = ''
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'chat_source_documents' not in st.session_state:
    st.session_state['chat_source_documents'] = []
if 'chat_context' not in st.session_state:
    st.session_state['chat_context'] = []
if 'chat_followup_questions' not in st.session_state:
    st.session_state['chat_followup_questions'] = []
if 'input_message_key' not in st.session_state:
    st.session_state ['input_message_key'] = 1

if 'do_not_process_question' not in st.session_state:
    st.session_state['do_not_process_question'] = False

chat_context_show_options = ('extracted context only', 'context within full source document')
if 'chat_context_show_option' not in st.session_state:
    st.session_state['chat_context_show_option'] = 'context within full source document'

if 'tab_context' not in st.session_state:
    st.session_state['tab_context'] = 'Not opened yet'
else:
    if st.session_state['chat_question'] != '' and st.session_state['tab_context'] != 'Not opened yet' and st.session_state['tab_context'] != 'Open_Queries':
        st.session_state['tab_context'] = 'Chat'

llm_helper = LLMHelper()


def ChangeButtonStyle(wgt_txt, wch_hex_colour = '#000000', wch_border_style = '', wch_textsize=''):
    htmlstr = """<script>
                    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
                    let backgroundColor = '#FFFFFF';
                    if (prefersDark) {{ backgroundColor = '#0E1117'; }}
                    var elements = window.parent.document.querySelectorAll('*'), i;
                    str_wgt_txt = '{wgt_txt}'
                    str_wgt_txt = str_wgt_txt.replace("/(^|[^\\])'/g", "$1\\'");
                    for (i = 0; i < elements.length; ++i)
                    {{ if (elements[i].innerText == str_wgt_txt) 
                        {{
                            parentNode = elements[i].parentNode;
                            element_type = elements[i].nodeName;
                            parent_type = parentNode.nodeName;
                            if (element_type == 'DIV' && parent_type == 'DIV') {{
                                // console.log(elements[i].parentNode.parentNode.nodeName);
                                elements[i].parentNode.parentNode.style.margin = "0"
                                elements[i].parentNode.parentNode.style.gap = "0"
                                }}
                            // console.log(str_wgt_txt + ' ( ' + element_type + ' ) : ' + parentNode + ' ( ' + parent_type + ' , ' + parentNode.innerText + ' )');
                            if (element_type == 'BUTTON') {{
                                elements[i].style.color  = '{wch_hex_colour}';
                                let border_style = '{wch_border_style}';
                                if (border_style.length > 0) {{
                                    elements[i].style.border ='{wch_border_style}';
                                    elements[i].style.outline ='{wch_border_style}';
                                    elements[i].addEventListener('focus', function() {{
                                        this.style.outline = '{wch_border_style}';
                                        this.style.boxShadow = '0px 0px 0px ' + backgroundColor;
                                        this.style.backgroundColor = '"' + backgroundColor + '"';
                                        // console.log(this.innerText + ' FOCUS');
                                        }});
                                    elements[i].addEventListener('hover', function() {{
                                        this.style.outline = '{wch_border_style}';
                                        this.style.boxShadow = '0px 0px 0px ' + backgroundColor;
                                        this.style.backgroundColor = '"' + backgroundColor + '"';
                                        // console.log(this.innerText + ' HOVER');
                                        }});
                                    }}
                                if ('{wch_textsize}' != '') {{
                                    elements[i].style.fontSize = '{wch_textsize}';
                                    }}
                            }}
                            else if (element_type == 'P' && '{wch_textsize}' != '') {{
                                elements[i].style.fontSize = '{wch_textsize}';
                                }}
                        }} }}
                        </script>  """

    htmlstr = htmlstr.format(wgt_txt=wgt_txt, wch_hex_colour=wch_hex_colour, wch_border_style=wch_border_style, wch_textsize=wch_textsize)
    components.html(f"{htmlstr}", height=0, width=0)


def questionAsked():
    st.session_state.chat_askedquestion = st.session_state["input"+str(st.session_state ['input_message_key'])]

# Display the context(s) associated with a source document used to andwer, with automaic scroll to the yellow highlighted context
def display_iframe(filename, link, contextList):
    st.session_state['do_not_process_question'] = True
    st.session_state['chat_askedquestion'] = st.session_state.chat_question
    if st.session_state['chat_context_show_option'] == 'context within full source document':
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
        <script>
            var frame = document.getElementById('{filename}');
            frame.onload = function() {{
                const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
                let textColor = '#222222';
                if (prefersDark) {{ textColor = '#EEEEEE'; }}
                var body = frame.contentWindow.document.querySelector('body');
                body.style.color = textColor;
            }};
        </script>
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


# Callback to assign the follow-up question is selected by the user
def ask_followup_question(followup_question):
    st.session_state['tab_context'] = 'Chat'  # Prevents side effect when first click after loading the page
    st.session_state.chat_askedquestion = followup_question
    st.session_state['input_message_key'] = st.session_state['input_message_key'] + 1

# Reset the right asked question to the input box when this page is reopened after switching to the OpenAI_Queries page
if st.session_state['tab_context'] != 'Chat' and st.session_state['chat_question'] != '' and st.session_state['chat_question'] != st.session_state['chat_askedquestion']:
    st.session_state['tab_context'] = 'Chat'
    st.session_state['do_not_process_question'] = True
    ask_followup_question(st.session_state['chat_question'])


# Chat 
clear_chat = st.button("Clear chat", key="clear_chat", on_click=clear_chat_data)
ChangeButtonStyle("Clear chat", "#ADCDE7", wch_border_style="none", wch_textsize="10px")

input_text = st.text_input("You: ", placeholder="type your question", value=st.session_state.chat_askedquestion, key="input"+str(st.session_state ['input_message_key']), on_change=questionAsked)


def show_document_source(filename, link, contextList):
    st.session_state['do_not_process_question'] = True
    display_iframe(filename, link, contextList)

# If a question is asked execute the request to get the result, context, sources and up to 3 follow-up questions proposals
if st.session_state.chat_askedquestion and st.session_state.do_not_process_question != True:
    st.session_state['chat_question'] = st.session_state.chat_askedquestion
    st.session_state.chat_askedquestion = ""
    st.session_state['chat_question'], result, context, sources = llm_helper.get_semantic_answer_lang_chain(st.session_state['chat_question'], st.session_state['chat_history'])
    result = llm_helper.clean_encoding(result)
    context = llm_helper.clean_encoding(context)
    result, chat_followup_questions_list = llm_helper.extract_followupquestions(result)
    st.session_state['chat_history'].append((st.session_state['chat_question'], result))
    st.session_state['chat_source_documents'].append(sources)
    st.session_state['chat_context'].append(context)
    st.session_state['chat_followup_questions'] = chat_followup_questions_list
    
st.session_state['do_not_process_question'] = False

# Displays the chat history
if st.session_state['chat_history']:
    history_range = range(len(st.session_state['chat_history'])-1, -1, -1)
    for i in range(len(st.session_state['chat_history'])-1, -1, -1):

        # This history entry is the latest one - also show follow-up questions, buttons to access source(s) context(s) 
        if i == history_range.start:
            answer_with_citations, sourceList, matchedSourcesList, linkList, filenameList = llm_helper.get_links_filenames(st.session_state['chat_history'][i][1], st.session_state['chat_source_documents'][i])
            st.session_state['chat_history'][i] = st.session_state['chat_history'][i][:1] + (answer_with_citations,)

            answer_with_citations = re.sub(r'\$\^\{(.*?)\}\$', r'(\1)', st.session_state['chat_history'][i][1]).strip() # message() does not get Latex nor html
            # message(answer_with_citations key=str(i))
            answer_message_height = int((len(answer_with_citations) / 22) * 1.1 * 8)
            st.text_area(label='', value=answer_with_citations, height=answer_message_height, key=str(i))
            st.write("<br>", unsafe_allow_html=True)

            # Display proposed follow-up questions which can be clicked on to ask that question automatically
            if len(st.session_state['chat_followup_questions']) > 0:
                st.markdown('**Proposed follow-up questions:**')
            with st.container():
                for questionId, followup_question in enumerate(st.session_state['chat_followup_questions']):
                    if followup_question:
                        str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)
                        st.button(str_followup_question, key=1000+questionId, on_click=ask_followup_question, args=(followup_question, ))

            if len(sourceList) > 0:
                st.write("<br><br>", unsafe_allow_html=True)
                # Selectbox to choose how to display the context(s) associated with the clicked source document name
                st.session_state['chat_context_show_option'] = st.selectbox(
                    'Choose how to display context used to answer the question when clicking on a document source below:',
                    chat_context_show_options,
                    index=chat_context_show_options.index(st.session_state['chat_context_show_option'])
                )

                # Buttons to display the context(s) associated with the clicked source document name
                for id in range(len(sourceList)):
                    st.button(f'({id+1}) {filenameList[id]}', key=filenameList[id], on_click=show_document_source, args=(filenameList[id], linkList[id], st.session_state['chat_context'][i][sourceList[id]], ))

                # Source Buttons Styles
                for id in range(len(sourceList)):
                    if filenameList[id] in matchedSourcesList:
                        ChangeButtonStyle(f'({id+1}) {filenameList[id]}', "#228822", wch_border_style='none', wch_textsize='10px')
                    else:
                        ChangeButtonStyle(f'({id+1}) {filenameList[id]}', "#AAAAAA", wch_border_style='none', wch_textsize='10px')


            for questionId, followup_question in enumerate(st.session_state['chat_followup_questions']):
                if followup_question:
                    str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)
                    ChangeButtonStyle(str_followup_question, "#5555FF", wch_border_style='none', wch_textsize='14px')


        # The old questions and answers within the history
        else:
            answer_with_citations = re.sub(r'\$\^\{(.*?)\}\$', r'(\1)', st.session_state['chat_history'][i][1]) # message() does not get Latex nor html
            message(answer_with_citations, key=str(i))
            st.markdown(f'\n\nSources: {st.session_state["chat_source_documents"][i]}')
            message(st.session_state['chat_history'][i][0], is_user=True, key=str(i) + '_user')
