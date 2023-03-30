import streamlit as st
import traceback
from utilities.helper import LLMHelper

def clear_summary():
    st.session_state['summary'] = ""

def get_custom_prompt():
    customtext = st.session_state['customtext']
    customprompt = "{}".format(customtext)
    return customprompt

def customcompletion():
    response = llm_helper.get_completion(get_custom_prompt(), max_tokens=500)
    st.session_state['result'] = response.encode().decode()

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

    llm_helper = LLMHelper()

    # displaying a box for a custom prompt
    st.session_state['customtext'] = st.text_area(label="Prompt",value='Legal clause: The Company and the Founders will provide the Investors with customary representations and warranties examples of which are set out in Appendix 4 and the Founders will provide the Investors with customary non-competition, non-solicitation and confidentiality undertakings.\n \n Plain English: The company and its founders will provide the usual assurances and guarantees on facts about the business. The founders will also agree not to work for competitors, poach employees or customers when they leave the company, and respect confidentiality. \n \n Legal clause: In the event of an initial public offering of the Companys shares on a US stock \n exchange the Investors shall be entitled to registration rights customary in transactions of this type (including two demand rights and unlimited shelf and piggy-back rights), with the expenses paid by the Company. \n \n Plain English: If the Company does an IPO in the USA, investors have the usual rights to include \n their shares in the public offering and the costs of doing this will be covered by the Company. \n \n Legal clause: Upon liquidation of the Company, the Series A Shareholders will receive in preference to all other shareholders an amount in respect of each Series A Share equal to one times the Original Issue Price (the "Liquidation Preference"), plus all accrued but unpaid dividends. To the extent that the Company has assets remaining after the distribution of that amount, the Series A Shareholders will participate with the holders of Ordinary Shares pro rata to the number of shares held on an as converted basis. \n \n Plain English:', height=400)
    st.button(label="Test with your own prompt", on_click=customcompletion)
    # displaying the summary
    result = ""
    if 'result' in st.session_state:
        result = st.session_state['result']
    st.text_area(label="OpenAI result", value=result, height=200)

except Exception as e:
    st.error(traceback.format_exc())
