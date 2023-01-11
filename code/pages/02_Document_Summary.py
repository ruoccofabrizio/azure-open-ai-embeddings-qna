import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils
import os

def summarize():
    _, response = utils.get_summary(get_prompt(), max_tokens=400, model='text-davinci-002')
    st.session_state['summary'] = response['choices'][0]['text'].encode().decode()

def clear_summary():
    st.session_state['summary'] = ""

def get_prompt():
    text = st.session_state['text']
    if text is None or text == '':
        text = '{}'
    if summary_type == "Basic Summary":
        prompt = "Summarize the following text:\n\n{}\n\nSummary:".format(text)
    elif summary_type == "Bullet Points":
        prompt = "Summarize the following text into bullet points:\n\n{}\n\nSummary:".format(text)
    elif summary_type == "Explain it to a second grader":
        prompt = "Explain the following text to a second grader:\n\n{}\n\nSummary:".format(text)

    return prompt

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

    # radio buttons for summary type
    summary_type = st.radio(
        "Select a type of summarization",
        ["Basic Summary", "Bullet Points", "Explain it to a second grader"],
        key="visibility"
    )
    # text area for user to input text
    st.session_state['text'] = st.text_area(label="Enter some text to summarize", height=400)
    st.button(label="Summarize", on_click=summarize)

    # if summary doesn't exist in the state, make it an empty string
    summary = ""
    if 'summary' in st.session_state:
        summary = st.session_state['summary']

    # displaying the summary
    st.text_area(label="Summary", value=summary, height=200)
    st.button(label="Clear summary", on_click=clear_summary)

    # displaying the prompt that was used to generate the summary
    st.text_area(label="Prompt",value=get_prompt(), height=400)
    st.button(label="Summarize with updated prompt")

except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )