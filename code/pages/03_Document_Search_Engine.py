import streamlit as st
import os
import re
import traceback
from utilities.helper import LLMHelper
import streamlit.components.v1 as components
import base64
import urllib
import pandas as pd
import random

# データの定義
SEARCH_QUERY = {"search_query": ""}

# ページ数を分割する正規表現を定義
pattern = r'(\S)p\.(\d+)'
if 'pdf_url' not in st.session_state:
    st.session_state.pdf_url = ""

def replace_link_title(original_link, new_title):
    # リンクのURL部分を抽出
    url_start = original_link.find("(")
    url_end = original_link.find(")")
    url = original_link[url_start+1:url_end]

    # 新しいタイトルでリンクを作成
    new_link = f"[{new_title}]({url})"
    return new_link

def displayPDF(file_url):
    # Embedding PDF in HTML
    pdf_display = F'<embed src={file_url} type="application/pdf" width="100%" height="1100px" />'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

# 検索履歴をセッションステートに保存する関数
def save_search_history(query):
    if 'search_history' not in st.session_state:
        st.session_state.search_history = pd.DataFrame(columns=['Search Query'])
    new_entry = {'Search Query': query}
    st.session_state.search_history = st.session_state.search_history.append(new_entry, ignore_index=True)

def update_pdf_url(pdf_url):
    st.session_state.pdf_url = pdf_url

def main():
    llm_helper_get_docs = LLMHelper()
    st.session_state['data_files'] = llm_helper_get_docs.blob_client.get_all_files()

    # st.session_state['data_files'] の filename をリスト化
    filenames = [d['filename'] for d in st.session_state['data_files']]

    col1, col2 = st.columns([4, 6])
    with col1:
        option = st.selectbox(
        '図書を選択してください',
        filenames)

        st.write('You selected:', option)

        # st.session_state['data_files'] の filename から converted_filename を取得
        embeddings = [d['embeddings'] for d in st.session_state['data_files'] if d['filename'] == option][0]

        query = st.text_input("キーワードを入力してください", value=SEARCH_QUERY["search_query"])


        # 検索ボタン
        if st.button("検索"):
            # ここで vector_store を指定して検索を実行
            save_search_history(query)
            llm_helper = LLMHelper(custom_prompt="", temperature=0.0, index_name=embeddings)
            st.session_state['question'], \
            st.session_state['response'], \
            st.session_state['context'], \
            st.session_state['sources'], \
            st.session_state['search_engine_results'] = llm_helper.get_semantic_answer_lang_chain_search_engine_hybrid(query, [])
            
        if 'search_engine_results' in st.session_state:
            st.write("検索結果：")
            for index, result in enumerate(st.session_state['search_engine_results']):
                
                button_key = f"button_{index}"

                st.button(result['search_title'], key=button_key, on_click=update_pdf_url, args=(f"{result['source']}&v={random.randint(1, 10000)}#page={result['page']}", ))
                st.write(f"{result['page_content']}")
                st.write("---")

    with col2:
        displayPDF(st.session_state.pdf_url)

if __name__ == "__main__":
    main()