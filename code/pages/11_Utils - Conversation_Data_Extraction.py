import streamlit as st
import os
import traceback
from utilities.helper import LLMHelper

def clear_summary():
    st.session_state['summary'] = ""

def get_custom_prompt():
    customtext = st.session_state['customtext']
    customprompt = "{}".format(customtext)
    return customprompt

def customcompletion():
    response = llm_helper.get_completion(get_custom_prompt())
    st.session_state['conv_result'] = response.encode().decode()

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

    llm_helper = LLMHelper()

    st.markdown("## Conversation data extraction")

    conversation_prompt = """   User: Hi there, I’m off between August 25 and September 11. I saved up 4000 for a nice trip. If I flew out from San Francisco, what are your suggestions for where I can go?
        Agent: For that budget you could travel to cities in the US, Mexico, Brazil, Italy or Japan. Any preferences?
        User: Excellent, I’ve always wanted to see Japan. What kind of hotel can I expect?
        Agent: Great, let me check what I have. First, can I just confirm with you that this is a trip for one adult?
        User: Yes it is
        Agent: Great, thank you, In that case I can offer you 15 days at HOTEL Sugoi, a 3 star hotel close to a Palace. You would be staying there between August 25th and September 7th. They offer free wifi and have an excellent guest rating of 8.49/10. The entire package costs 2024.25USD. Should I book this for you?
        User: That sounds really good actually. Lets say I have a date I wanted to bring…would Japan be out of my price range then?
        Agent: Yes, unfortunately the packages I have for two in Japan do not fit in your budget. However I can offer you a 13 day beach getaway at the 3 star Rose Sierra Hotel in Santo Domingo. Would something like that interest you?
        User: How are the guest ratings for that place?
        Agent: 7.06/10, so guests seem to be quite satisfied with the place.
        User: TRUE. You know what, I’m not sure that I’m ready to ask her to travel with me yet anyway. Just book me for Sugoi
        Agent:I can do that for you! 
        User:Thanks!
        Agent: Can I help you with some other booking today?
        User:No, thanks!


        Execute these tasks:
        -	Summarize the conversation, key: summary
        -      Customer budget none if not detected, key: budget
        -      Departure city, key: departure
        -      Destination city, key: destination
        -      Selected country, key: country
        -      Which hotel the customer choose?, key: hotel
        -	Did the agent remind the customer about the evaluation survey? , key:evaluation true or false as bool
        -	Did the customer mention a product competitor?, key: competitor true or false as bool
        -	Did the customer ask for a discount?, key:discount true or false as bool
        - Agent asked for additional customer needs. key: additional_requests
        - Was the customer happy with the resolution? key: satisfied

        Answer in JSON machine-readable format, using the keys from above.
        Format the ouput as JSON object called "results". Pretty print the JSON and make sure that is properly closed at the end."""

    # displaying a box for a custom prompt
    st.session_state['customtext'] = st.text_area(label="Prompt",value=conversation_prompt, height=400)
    st.button(label="Execute tasks", on_click=customcompletion)
    # displaying the summary
    result = ""
    if 'conv_result' in st.session_state:
        result = st.session_state['conv_result']
    st.text_area(label="OpenAI result", value=result, height=200)

except Exception as e:
    st.error(traceback.format_exc())
