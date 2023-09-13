import streamlit as st
import os
import re
import traceback
from utilities.helper import LLMHelper

# データの定義
SEARCH_QUERY = {"search_query": "秋においしい食べ物を教えて"}
SEARCH_RESULTS = [
    {"result": "鮭", "url": "https://streamlit.io/", "digest": "鮭は秋に旬を迎える魚で..."},
    {"result": "栗", "url": "https://docs.streamlit.io/", "digest": "栗は秋に旬を迎える果物で..."}
]

pattern = r'(\S)p\.(\d+)'
# def return_query_result(llm_helper ,query):
#     # この例では、検索クエリに基づいて結果をフィルタリングするロジックは実装していません。
#     # 必要に応じて、検索ロジックをここに追加してください。
#     llm_helper.get_semantic_answer_lang_chain(query, [])
#     return SEARCH_RESULTS

def main():
    llm_helper = LLMHelper(custom_prompt="", temperature=0.0)

    st.title("文章検索エンジン")

    query = st.text_input("キーワードを入力してください", value=SEARCH_QUERY["search_query"])


    # 検索ボタン
    if st.button("検索"):
        st.session_state['question'], \
        st.session_state['response'], \
        st.session_state['context'], \
        st.session_state['sources'], \
        st.session_state['search_engine_results'] = llm_helper.get_semantic_answer_lang_chain_search_engine(query, [])
        
        # results = return_query_result(query)
        st.write("検索結果：")
        for result in st.session_state['search_engine_results']:
            title = re.sub(pattern, r'\1 \2ページ', result['source'])
            st.write(f"### {title}")
            st.write(f"{result['page_content']}")
            # st.write(f"{result['page_content'][:90]}")
            st.write("---")

if __name__ == "__main__":
    main()