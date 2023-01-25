import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils
import os

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

def get_custom_prompt():
    customtext = st.session_state['customtext']
    customprompt = "{}".format(customtext)
    return customprompt

def summarize():
    _, response = utils.get_completion(get_prompt(), max_tokens=500, model='davinci-002')
    st.session_state['summary'] = response['choices'][0]['text'].encode().decode()

def customcompletion():
    _, response = utils.get_completion(get_custom_prompt(), max_tokens=500, model='davinci-002')
    st.session_state['result'] = response['choices'][0]['text'].encode().decode()

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

    st.markdown("## Bring your own prompt")

    # displaying a box for a custom prompt
    st.session_state['customtext'] = st.text_area(label="Prompt",value='Legal clause: The Company and the Founders will provide the Investors with customary representations and warranties examples of which are set out in Appendix 4 and the Founders will provide the Investors with customary non-competition, non-solicitation and confidentiality undertakings.\n \n Plain English: The company and its founders will provide the usual assurances and guarantees on facts about the business. The founders will also agree not to work for competitors, poach employees or customers when they leave the company, and respect confidentiality. \n \n Legal clause: In the event of an initial public offering of the Companys shares on a US stock \n exchange the Investors shall be entitled to registration rights customary in transactions of this type (including two demand rights and unlimited shelf and piggy-back rights), with the expenses paid by the Company. \n \n Plain English: If the Company does an IPO in the USA, investors have the usual rights to include \n their shares in the public offering and the costs of doing this will be covered by the Company. \n \n Legal clause: Upon liquidation of the Company, the Series A Shareholders will receive in preference to all other shareholders an amount in respect of each Series A Share equal to one times the Original Issue Price (the "Liquidation Preference"), plus all accrued but unpaid dividends. To the extent that the Company has assets remaining after the distribution of that amount, the Series A Shareholders will participate with the holders of Ordinary Shares pro rata to the number of shares held on an as converted basis. \n \n Plain English:', height=400)
    st.button(label="Test with your own prompt", on_click=customcompletion)
    # displaying the summar
    result = ""
    if 'result' in st.session_state:
        result = st.session_state['result']
    st.text_area(label="OpenAI result", value=result, height=200)

    st.markdown("## Summarization")
    # radio buttons for summary type
    summary_type = st.radio(
        "Select a type of summarization",
        ["Basic Summary", "Bullet Points", "Explain it to a second grader"],
        key="visibility"
    )
    # text area for user to input text
    st.session_state['text'] = st.text_area(label="Enter some text to summarize",value='A neutron star is the collapsed core of a massive supergiant star, which had a total mass of between 10 and 25 solar masses, possibly more if the star was especially metal-rich.[1] Neutron stars are the smallest and densest stellar objects, excluding black holes and hypothetical white holes, quark stars, and strange stars.[2] Neutron stars have a radius on the order of 10 kilometres (6.2 mi) and a mass of about 1.4 solar masses.[3] They result from the supernova explosion of a massive star, combined with gravitational collapse, that compresses the core past white dwarf star density to that of atomic nuclei.', height=200)
    st.button(label="Summarize", on_click=summarize)

    # if summary doesn't exist in the state, make it an empty string
    summary = ""
    if 'summary' in st.session_state:
        summary = st.session_state['summary']

    # displaying the summary
    st.text_area(label="Summary result", value=summary, height=200)
    st.button(label="Clear summary", on_click=clear_summary)



except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
