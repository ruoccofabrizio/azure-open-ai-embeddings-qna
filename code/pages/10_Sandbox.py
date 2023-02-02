import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils
import os



def clear_text():
    st.session_state['text'] = ""
    st.session_state['result'] = ""
    st.session_state['customtext'] = ""
    st.session_state['summresult'] = ""

def get_custom_prompt():
    customtext = st.session_state['customtext']
    customprompt = "{}".format(customtext)
    return customprompt

def customcompletion():
    _, response = utils.get_completion(get_custom_prompt(), max_tokens=500, model=os.getenv('OPENAI_ENGINES', 'text-davinci-003'))
    st.session_state['result'] = response['choices'][0]['text'].encode().decode()

def summcompletions():
    _, response = utils.get_completion(summtext, max_tokens=500, model=os.getenv('OPENAI_ENGINES', 'text-davinci-003'))
    st.session_state['summresult'] = response['choices'][0]['text'].encode().decode()


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
    st.session_state['customtext'] = st.text_area(label="Prompt",value='Legal clause: The Company and the Founders will provide the Investors with customary representations and warranties examples of which are set out in Appendix 4 and the Founders will provide the Investors with customary non-competition, non-solicitation and confidentiality undertakings.\n \n Plain English: The company and its founders will provide the usual assurances and guarantees on facts about the business. The founders will also agree not to work for competitors, poach employees or customers when they leave the company, and respect confidentiality. \n \n Legal clause: In the event of an initial public offering of the Companys shares on a US stock exchange the Investors shall be entitled to registration rights customary in transactions of this type (including two demand rights and unlimited shelf and piggy-back rights), with the expenses paid by the Company. \n \n Plain English: If the Company does an IPO in the USA, investors have the usual rights to include \n their shares in the public offering and the costs of doing this will be covered by the Company. \n \n Legal clause: Upon liquidation of the Company, the Series A Shareholders will receive in preference to all other shareholders an amount in respect of each Series A Share equal to one times the Original Issue Price (the "Liquidation Preference"), plus all accrued but unpaid dividends. To the extent that the Company has assets remaining after the distribution of that amount, the Series A Shareholders will participate with the holders of Ordinary Shares pro rata to the number of shares held on an as converted basis. \n \n Plain English:', height=400)
    st.button(label="Test with your own prompt", on_click=customcompletion)

    result = ""
    if 'result' in st.session_state:
        result = st.session_state['result']
    st.text_area(label="OpenAI result", value=result, height=200)
    st.button(label="Clear result", on_click=clear_text)    

    st.markdown("## Summarization")
    summtext = st.text_area(label="Prompt",value="Please extract the following information from the phone conversation below: \n 1. Call reason (key: reason) \n 2. Cause of the incident (key: cause) \n 3. Names Of all drivers an array (key: driver_names) \n 4. Insurance number (key: insurance_number) \n 5. Accident location (key: location) \n 6. Car damages (key: damages)  \n 7. A short yet detailed summary in Spanish (key: summary) Make sure fields 1 to 6 are as short as possible (e.g. for location just say the location name). Please answer in JSON machine-readable format, using the keys from the description \n \nCustomer conversation: \"Hi I just had a car accident and wanted to report it, OK. I hope you are alright, what happened? I was driving on the I-18 and I damaged my car. That is understandable. Can you give me your full name? Sure, it is Sarah Parker. DO you know what caused the accident? I think I might have hit a pothole, OK, Where did the accident take place? On the I-18 freeway. Was anyone injured? I do not think so, but not sure. OK, well we will need to do an investigation. Can you give me the other drivers information? Sure. his name is John Radley. And your insurance number please. OK... Give me a minute. OK. it is 546452. OK, what type of damages has the car? Headlights are broken and the airbags went off. Are you going to be able to drive it? not sure. I am going to have to have it towed. Well, we will need to get it inspected. I will go ahead and start the claim and in parallel send you the assistance tow truck. Thank you\"", height=300)
    st.button(label="Summarize", on_click=summcompletions)

    summresult = ""
    if 'summresult' in st.session_state:
        summresult = st.session_state['summresult']
    st.text_area(label="OpenAI results", value=summresult, height=300)

except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
