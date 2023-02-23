import streamlit as st
from helper import get_semantic_answer

# st.set_page_config(layout="wide")
hide_menu_style = """<style>#MainMenu {visibility: hidden;}</style>"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.image('./microsoft.png', width=200)
st.title('Azure OpenAI Service Q&A Demo')
st.caption('Sponsored by Microsoft\'s Global Black Belt team for AI in EMEA')
st.write('This demo shows how Azure OpenAI Service can be used to answer questions on unstructured data. It was trained on the 10K form dataset. Under the hood, we use OpenAI\'s GPT-3 models and embeddings to generate answers to the users\' questions.')

tab1, tab2, tab3 = st.tabs(["Demo", "Sample questions", "How does this demo work?"])

with tab1:
    st.write('Try asking a question like:\n\nWhat is Azure? Give me a long answer!')
    question = st.text_input("Question:")

    if question != '':
        answer, prompt = get_semantic_answer(question)
        st.write(f"**Question:** {question}")
        st.write(f"**Answer:** {answer}")
        with st.expander("Click here to see the prompt we've used to generate the answer", expanded=False):
            prompt = prompt.replace('$', '\$')
            st.markdown(f":star: **Short explanation**\n1. The first part of the prompt is the retrieved documents that were likely to contain the answer\n1. The second part is the actual prompt to answer our question\n\n:star: **Prompt:**\n{prompt}")
with tab2:
    st.write('Try asking questions like:')
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown("""
* What's Microsoft's mission? Give me a long answer!
* What licenses Microsoft offers?
* What's an Enterprise Agreement?
* Tell me more about Microsoft execs
* Who's Amy Hood? how long in role? and previously?""")

    with col2:
        st.markdown("""
* Who's Amy Hood? how long in role? and previously?
* What Microsoft mean with Intelligent Cloud?
* Where does Github sit in Microsoft portfolio?
* Which are Microsoft competitors in intelligent cloud business?
* What's microsoft commitment to inclusion?""")

    st.write("If you want a shorter answer, you can say \"Write a short answer\" or do the opposite and say \"Give me a long answer\".")
    st.write("You can also ask questions in other languages, e.g., try to ask a question in German or Spanish.")

with tab3:
   st.header("How does this demo work?")
   st.markdown("""
               This demo leverages the following components to achieve a ChatGPT-like experience on unstructured documents:
               * **Azure OpenAI Service** to generate answers to questions
               * **Azure OpenAI Service Embeddings** to semantically extract the "meaning of a document"
               * **RediSearch** to store the embeddings and perform search queries
               * **Azure Form Recognizer** to extract the text from the documents
               """)
   st.image("./architecture.png", caption="Solution Architecture")
   st.markdown("""
               So, what is happening here? Let's break it down:
               1. Firstly, we parse the documents in our knowledge base and extract the text using Azure Form Recognizer. We do this since data might be in PDF format, but it also allows to create smaller text chunks. We do not want to work on documents that are 100's of pages long.
               1. Next, we use Azure OpenAI Service Embeddings to semantically extract the "meaning of a document". This converts the sections of each document into a vector (basically a long series of numbers, 1536 to be more precise), which represents the semantics of each document section. We store this vector in RediSearch.
               1. As the user asks a question, we again use Azure OpenAI Service Embeddings to semantically extract the "meaning of the question". We then use RediSearch to find the most similar documents to the question. In our case, we use the top 3 documents. These documents are likely to contain the answer to our question.
               1. Now that we have the matching documents, we use Azure OpenAI Service to generate an answer to our question. To do this, we use the top 3 documents as the context to generate the answer, given the original question of the user. You can see this prompt when you click on the "Click here to see the prompt we've used to generate the answer" link.
               1. Finally, we return the answer to the user. Done!
               """)