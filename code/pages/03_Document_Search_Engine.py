import streamlit as st
import os
import re
import traceback
from utilities.helper import LLMHelper

# データの定義
SEARCH_QUERY = {"search_query": ""}

# ページ数を分割する正規表現を定義
pattern = r'(\S)p\.(\d+)'

def replace_link_title(original_link, new_title):
    # リンクのURL部分を抽出
    url_start = original_link.find("(")
    url_end = original_link.find(")")
    url = original_link[url_start+1:url_end]

    # 新しいタイトルでリンクを作成
    new_link = f"[{new_title}]({url})"
    return new_link

def main():
    llm_helper = LLMHelper(custom_prompt="", temperature=0.0)

    st.title("文章検索エンジン v2")

    query = st.text_input("キーワードを入力してください", value=SEARCH_QUERY["search_query"])


    # 検索ボタン
    if st.button("検索"):
        st.session_state['question'], \
        st.session_state['response'], \
        st.session_state['context'], \
        st.session_state['sources'], \
        st.session_state['search_engine_results'] = llm_helper.get_semantic_answer_lang_chain_search_engine(query, [])
        
        st.write("検索結果：")
        
        for result in st.session_state['search_engine_results']:
            # print(result)
            title = re.sub(pattern, r'\1 \2ページ', result['source'])
            
            # title = replace_link_title(result['source'], result["search_title"])
            # print(replace_link_title(result['source'], result["search_title"]))
            st.write(f"### {result['source']}")
            st.write(f"{result['page_content']}")
            st.write("---")

if __name__ == "__main__":
    main()